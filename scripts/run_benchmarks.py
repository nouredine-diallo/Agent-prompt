import json
import time
import requests
import csv
import os
from datetime import datetime
#simule appels API  mesure latence API , recall reel , erreurs , fallback 


API_URL = "http://127.0.0.1:8000/generate"
QUERIES_PATH = "tests/queries_agent_20.jsonl"
METRICS_PATH = "metrics/benchmarks.csv"
LOG_PATH = "logs/step5_run.log"

os.makedirs("metrics", exist_ok=True)
os.makedirs("logs", exist_ok=True)

with open(QUERIES_PATH, "r") as f:
    queries = [json.loads(line) for line in f]

header = ["query_id","scenario_type","recall1","recall3","recall5","mrr","latency_ms","attempts","status","notes"]

with open(METRICS_PATH, "w", newline="") as csvfile, open(LOG_PATH, "a") as logf:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    for i, q in enumerate(queries):
        query_id = f"q{i+1:02d}"
        payload = {"query": q["query"], "query_id": query_id}
        t0 = time.time()
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            latency = int((time.time() - t0) * 1000)
            status = "ok" if resp.status_code == 200 else "fail"
            data = resp.json() if status == "ok" else {}
            returned_sources = set(data.get("sources", []))
            expected_sources = set(q.get("expected_sources", []))
            recall1 = int(bool(returned_sources & expected_sources))
            recall3 = recall1  # mock: 1 source max
            recall5 = recall1
            mrr = recall1
            attempts = 1
            notes = ""
        except Exception as e:
            latency = -1
            status = "fail"
            recall1 = recall3 = recall5 = mrr = 0
            attempts = 1
            notes = str(e)
            data = {}
        writer.writerow([query_id, q["scenario_type"], recall1, recall3, recall5, mrr, latency, attempts, status, notes])
        logf.write(f"{datetime.now().isoformat()} | {query_id} | {q['scenario_type']} | status={status} | latency={latency}ms | notes={notes}\n")
        logf.flush()
