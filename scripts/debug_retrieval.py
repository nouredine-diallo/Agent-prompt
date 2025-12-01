# scripts/debug_retrieval.py
from src.ingestion import model, collection
import json, sys

q = sys.argv[1] if len(sys.argv)>1 else "q08's text here"
k = int(sys.argv[2]) if len(sys.argv)>2 else 10

q_emb = model.encode([q], convert_to_numpy=True)
res = collection.query(query_embeddings=q_emb.tolist(), n_results=k, include=["documents","metadatas","distances"])
for i, doc in enumerate(res["documents"][0]):
    meta = res["metadatas"][0][i]
    dist = res["distances"][0][i]
    print(f"RANK {i+1} | dist={dist:.4f} | source={meta.get('title') or meta.get('source')}")
    print(doc[:500].replace('\n',' ') + "\n---\n")
