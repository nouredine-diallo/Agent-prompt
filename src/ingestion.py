import os
import glob
import json
import sys
import nltk
import chromadb
from typing import List
try:
    from langdetect import detect
except ImportError:
    def detect(text):
        return "und"
from datetime import datetime
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import argparse
import nltk
import ssl


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Téléchargement automatique des paquets nltk requis
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Config
SRC_MAP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "source_map.json")
MODEL = "all-MiniLM-L6-v2"
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "txt")
CHUNK_SIZE = 200  # words
OVERLAP = 50

# Init
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

model = SentenceTransformer(MODEL)
client = chromadb.PersistentClient(path=DB_DIR)
col = client.get_or_create_collection("docs")
collection = col

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"Read error: {path} - {e}", file=sys.stderr)
        return ""

def chunk_text(txt: str, target: int, overlap: int) -> List[str]:
    """decoupe les texte en chunks et on utilise un overlap pour eviter les coupures de phrases brute et obtnir plus de contexte """
    sents = sent_tokenize(txt)
    chunks = []
    curr = []
    curr_words = 0
    
    for s in sents:
        words = s.split()
        wc = len(words)
        
        if curr_words + wc <= target or not curr:
            curr.append(s)
            curr_words += wc
        else:
            chunks.append(" ".join(curr))
            # Gestion de l'overlap entre chunks pour recup le context 
            if overlap > 0:
                overlap_txt = " ".join(" ".join(curr).split()[-overlap:])
                curr = [overlap_txt, s] if overlap_txt else [s]
                curr_words = len(overlap_txt.split()) + wc
            else:
                curr = [s]
                curr_words = wc
    
    if curr:
        chunks.append(" ".join(curr))
    return chunks

def ingest(src_dir: str = DOCS_DIR, chunk_sz: int = CHUNK_SIZE, overlap: int = OVERLAP):
    "map les source pour garder une trace , fais l'embedding et stock ses vecteur dans ChromaDB"
    print(f"Starting ingestion from {src_dir}")
    files = glob.glob(os.path.join(src_dir, "*.txt"))
    
    if not files:
        print(f"No .txt files in {src_dir}. Did you run fetch_data.py?", file=sys.stderr)
        return
    
    print(f"Found {len(files)} files")
    docs, metas, ids = [], [], []
    
    # Load source mapping
    src_map = {}
    if os.path.exists(SRC_MAP):
        with open(SRC_MAP, "r", encoding="utf-8") as f:
            src_map = json.load(f)
    
    for fpath in files:
        txt = read_file(fpath)
        if not txt.strip():
            print(f"  Skip empty: {fpath}")
            continue
        
        title = os.path.basename(fpath)
        chunks = chunk_text(txt, target=chunk_sz, overlap=overlap)
        meta_info = src_map.get(title, {})
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{title}--{i}"
            
            # Skip if exists
            if col.get(ids=[doc_id])['ids']:
                continue
            
            ids.append(doc_id)
            
            # Detect language 
            try:
                lang = detect(chunk)
            except:
                lang = "und"
            
            meta = {
                "source": fpath,
                "title": title,
                "chunk": i,
                "ingested_at": datetime.utcnow().isoformat(),
                "source_url": meta_info.get("source_url", ""),
                "original_filename": meta_info.get("original_file", ""),
                "language": lang,
                "author": meta_info.get("author", "")
            }
            metas.append(meta)
            docs.append(chunk)
    
    if not docs:
        print("Nothing new to ingest")
        return
    #embedding des chunks ( vectorisation)
    print(f"Embedding {len(docs)} chunks...")
    embeddings = model.encode(docs, show_progress_bar=True, convert_to_numpy=True)
    # on stock ses vecteur dans la bd ChromaDB
    print("Adding to ChromaDB...")
    batch = 5000
    for i in range(0, len(ids), batch):
        col.add(
            ids=ids[i:i+batch],
            documents=docs[i:i+batch],
            metadatas=metas[i:i+batch],
            embeddings=embeddings.tolist()[i:i+batch]
        )
    
    print(f"Done. DB at {DB_DIR}")

def test_retrieval(q: str, k: int = 5):
    """ Transforme une query en vecteur , recherche dans chroma db les distance le splus proche et retourne les doc les plus proche"""
    print(f"\nTesting RAG: '{q}'") #transforme query en vecteur ( embedding)
    q_emb = model.encode([q], convert_to_numpy=True)
    
    try:  #recherche de similarités par chromaDB ( cosin distance)
        res = col.query(
            query_embeddings=q_emb.tolist(),
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )  
    except Exception as e:
        print(f"Query failed: {e}. Empty DB?", file=sys.stderr)
        return None
    
    if not res.get("documents") or not res["documents"][0]:
        print("No results found")
        return None
    
    for i, doc in enumerate(res["documents"][0]):  #pour chaque doc on donne les metadata des docs ainsi que la distance calcule precedemment 
        meta = res["metadatas"][0][i]
        dist = res["distances"][0][i]
        print(f"\n[{i+1}] dist={dist:.4f} | {meta.get('title', 'N/A')}")
        print(f"{doc[:300]}...")
    
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk', type=int, default=CHUNK_SIZE, help='Chunk size (words)')
    parser.add_argument('--overlap', type=int, default=OVERLAP, help='Overlap (words)')
    args = parser.parse_args()
    
    ingest(chunk_sz=args.chunk, overlap=args.overlap)
    test_retrieval("prompt engineering best practices", k=3)
    test_retrieval("what is chain of thought?", k=3)
