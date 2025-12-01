import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python compute_metrics.py metrics/benchmarks.csv")
    sys.exit(1)

csv_path = sys.argv[1]
df = pd.read_csv(csv_path)

print("--- Résumé métriques ---")
print(df[['recall1','recall3','recall5','mrr']].mean())
print("fallback_rate:", (df['status']!='ok').mean())
print("latency_ms mean:", df['latency_ms'].mean())
