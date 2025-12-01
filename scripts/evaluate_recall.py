#!/usr/bin/env python3
# scripts/evaluate_recall.py
# Usage: python scripts/evaluate_recall.py --queries queries.jsonl --k 5

import argparse
import os
import pandas as pd
import sys

def lazy_imports():
    global json, chromadb, np, SentenceTransformer
    import json
    import numpy as np
    from chromadb.config import Settings
    import chromadb
    from sentence_transformers import SentenceTransformer

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROMA_DIR = os.path.join(BASE, "chroma_db")
EMBED_MODEL = "all-MiniLM-L6-v2"

def load_queries(path):
    lazy_imports()
    q = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            q.append(obj)
    return q

def evaluate(queries, k=5):
    lazy_imports()
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("docs")
    model = SentenceTransformer(EMBED_MODEL)
    total = len(queries)
    hits = 0
    mrr_total = 0.0
    for q in queries:
        query = q["query"]
        expected = q.get("expected", [])
        q_emb = model.encode([query], convert_to_numpy=True).tolist()
        res = col.query(query_embeddings=q_emb, n_results=k, include=["metadatas"])
        ids = res.get("ids", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        found = False
        rank = None
        for idx, meta in enumerate(metas):
            src = meta.get("source") or meta.get("title") or ids[idx]
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
        else:
            mrr_total += 0.0
    recall = hits / total if total>0 else 0.0
    mrr = mrr_total / total if total>0 else 0.0
    print(f"Queries: {total}, Recall@{k}: {recall:.3f}, MRR: {mrr:.3f}")
    return {"queries": total, "recall": recall, "mrr": mrr}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=str, default=None, help="Path to queries JSONL file for embedding-based evaluation.")
    parser.add_argument("--k", type=int, default=5, help="Top-k for recall evaluation.")
    parser.add_argument("--csv", type=str, default=None, help="Path to CSV file for summary metrics (benchmarks.csv).")
    args = parser.parse_args()


    # Embedding-based evaluation (if queries provided and not empty string)
    if args.queries and args.queries.strip():
        qs = load_queries(args.queries)
        evaluate(qs, k=args.k)

    # CSV summary metrics (if csv provided)
    csv_path = args.csv or "metrics/benchmarks.csv"
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print("--- Résumé Recall/MRR ---")
        print("Recall@1:", df['recall1'].mean())
        print("Recall@3:", df['recall3'].mean())
        print("Recall@5:", df['recall5'].mean())
        print("MRR:", df['mrr'].mean())
        print("Fallback rate:", (df['status']!='ok').mean())
        print("Latence moyenne (ms):", df['latency_ms'].mean())
    else:
        print(f"[INFO] CSV file not found or not provided: {csv_path}. Skipping summary metrics.")
