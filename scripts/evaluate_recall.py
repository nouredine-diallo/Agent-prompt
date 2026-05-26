#EVALUE LE RAG 
#On fait un embedding de query et compare a ce qui est present dans la chromaDB ? 1 = identique 0.8 proche 0.3 eloigne
import argparse
import os
import json
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_queries(path):
    q = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            q.append(json.loads(line))
    return q

def evaluate(queries, k=5):
    
    import sys
    sys.path.append(BASE)
    from src.agent_core import _retrieve_documents

    total = len(queries)
    hits = 0
    mrr_total = 0.0
    
    print(f"Évaluation Hybride RAG sur {total} requêtes...")

    for q in queries:
        query = q["query"]
        
        expected = q.get("expected") or q.get("expected_sources") or []
        
        # CHROMA + RERANKER
        docs, metas = _retrieve_documents(query, k=k)
        
        found = False
        rank = None
        
        for idx, meta in enumerate(metas):
            src = meta.get("source") or meta.get("title") or ""
            for e in expected:
                if e in src:
                    found = True
                    rank = idx + 1
                    break
            if found:
                break
                
        if found:
            hits += 1
            mrr_total += 1.0 / rank

    recall = hits / total if total>0 else 0.0
    mrr = mrr_total / total if total>0 else 0.0
    print(f"\n--- RÉSULTATS HYBRID RAG ---")
    print(f"Queries: {total}")
    print(f"Recall@{k}: {recall:.3f}")
    print(f"MRR: {mrr:.3f}")
    return {"queries": total, "recall": recall, "mrr": mrr}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=str, default="tests/queries_agent_20.jsonl", help="Path to queries JSONL")
    parser.add_argument("--k", type=int, default=5, help="Top-k for recall evaluation")
    args = parser.parse_args()

    evaluate(load_queries(args.queries), k=args.k)