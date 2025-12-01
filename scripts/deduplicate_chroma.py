#!/usr/bin/env python3
# scripts/deduplicate_chroma.py
# Supprime near-duplicates dans Chroma (cosine similarity)
# Usage: python scripts/deduplicate_chroma.py --threshold 0.92 --batch 500

import os
import argparse
import shutil
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.config import Settings
import math
import time

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROMA_DIR = os.path.join(BASE, "chroma_db")
BACKUP_DIR = os.path.join(BASE, "chroma_db_backup_" + time.strftime("%Y%m%dT%H%M%S"))

def backup_chroma():
    if os.path.exists(CHROMA_DIR):
        print("Backing up chroma_db to", BACKUP_DIR)
        shutil.copytree(CHROMA_DIR, BACKUP_DIR)
    else:
        print("No chroma_db directory found; skipping backup.")

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("docs")
    return col

def load_all_embeddings(collection):
    print("Fetching all ids and embeddings from Chroma...")
    res = collection.get(include=["embeddings", "metadatas", "documents"])
    ids = res.get("ids", [])
    if isinstance(ids, list) and len(ids) == 1:
        ids = ids[0]
    embeddings = res.get("embeddings", [])
    if isinstance(embeddings, list) and len(embeddings)==1:
        embeddings = embeddings[0]
    emb_arr = np.array(embeddings, dtype=np.float32)
    return ids, emb_arr

def chunked_indices(n, batch):
    for i in range(0, n, batch):
        yield i, min(n, i+batch)

def dedup(collection, threshold=0.92, batch_size=500):
    ids, emb = load_all_embeddings(collection)
    n = emb.shape[0]
    print(f"Loaded {n} embeddings.")
    if n == 0:
        print("No embeddings found. Exiting.")
        return
    to_delete = set()
    for i0, i1 in chunked_indices(n, batch_size):
        block = emb[i0:i1]
        sim = cosine_similarity(block, emb)
        for i_local, row in enumerate(sim):
            i_global = i0 + i_local
            row[i_global] = -1.0
            dup_indices = np.where(row >= threshold)[0]
            for j in dup_indices:
                keep = min(i_global, j)
                drop = max(i_global, j)
                if drop not in to_delete and keep not in to_delete:
                    to_delete.add(drop)
        print(f"Processed block {i0}-{i1}, marked {len(to_delete)} to delete so far.")
    to_delete_ids = [ids[idx] for idx in sorted(to_delete)]
    print(f"Total duplicates to delete: {len(to_delete_ids)}")
    if len(to_delete_ids) > 0:
        print("Deleting duplicates from collection...")
        collection.delete(ids=to_delete_ids)
    print("Deduplication complete.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.92, help="cosine similarity threshold to treat as duplicate")
    parser.add_argument("--batch", type=int, default=500, help="batch size for block comparisons")
    args = parser.parse_args()

    backup_chroma()
    col = get_collection()
    dedup(col, threshold=args.threshold, batch_size=args.batch)

if __name__ == "__main__":
    main()
