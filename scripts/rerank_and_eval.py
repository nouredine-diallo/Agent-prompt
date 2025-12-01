import sys, os, json, csv
sys.path.insert(0, os.path.abspath('.'))
from src.ingestion import model, collection
from sentence_transformers import CrossEncoder, util
import numpy as np

CE_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

def retrieve_top_n(query, n=50):
    q_emb = model.encode([query], convert_to_numpy=True)
    res = collection.query(query_embeddings=q_emb.tolist(), n_results=n, include=["documents","metadatas","distances"])
    docs = res.get("documents",[[]])[0]
    metas = res.get("metadatas",[[]])[0]
    return docs, metas

def rerank(query, docs):
    ce = CrossEncoder(CE_MODEL)
    pairs = [(query, d) for d in docs]
    scores = ce.predict(pairs)
    idxs = np.argsort(scores)[::-1]
    return idxs, scores

def evaluate_one(query, expected_sources, k=5):
    docs, metas = retrieve_top_n(query, n=50)
    idxs, scores = rerank(query, docs)
    returned_sources = [metas[i].get("title") or metas[i].get("source") for i in idxs[:k]]
    recall_k = 1 if any(s in (returned_sources) for s in expected_sources) else 0
    rank = None
    for pos, i in enumerate(idxs[:50], start=1):
        src = metas[i-1].get("title") or metas[i-1].get("source")
        if src in expected_sources:
            rank = pos
            break
    mrr = 1.0/rank if rank else 0.0
    return recall_k, mrr, returned_sources[:k]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/rerank_and_eval.py queries.jsonl metrics_out.csv")
        sys.exit(1)
    queries_file = sys.argv[1]
    out_csv = sys.argv[2]
    rows = []
    with open(queries_file, "r", encoding="utf-8") as f:
        for line in f:
            qobj = json.loads(line)
            qid = qobj.get("id") or qobj.get("query_id")
            query = qobj["query"]
            expected = qobj.get("expected_sources", [])
            recall, mrr, returned = evaluate_one(query, expected, k=5)
            rows.append([qid, recall, mrr, ",".join(map(str,returned))])
    with open(out_csv, "w", newline='', encoding='utf-8') as w:
        writer = csv.writer(w)
        writer.writerow(["query_id","recall5","mrr","returned_sources"])
        writer.writerows(rows)
    print("Done. Results:", out_csv)
