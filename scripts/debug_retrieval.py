
#vérifier si tes embeddings sont bons, verifier que les docs sont bon , debug la qualité du rag ( pertinence des result) , affiche les distance 
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.agent_core import _retrieve_documents

q = sys.argv[1] if len(sys.argv)>1 else "prompt injection defense"
k = int(sys.argv[2]) if len(sys.argv)>2 else 5

print(f"\n- DEBUGGING  RETRIEVAL (Chroma + Cross-Encoder) ")
print(f"Query: '{q}'\n")


docs, metas = _retrieve_documents(q, k=k)

if not docs:
    print("Aucun document trouvé.")
    sys.exit()

for i, doc in enumerate(docs):
    meta = metas[i]
    source = meta.get('title') or meta.get('source') or "Source Inconnue"
    print(f"RANK {i+1} | source={source}")
    print(doc[:300].replace('\n',' ') + "...\n---\n")