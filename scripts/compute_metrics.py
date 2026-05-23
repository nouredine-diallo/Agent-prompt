import pandas as pd
import sys

#Tableau de performance , recall : le bon doc est dans le top ? MRR la position du bon document ,fallback_rate : combien de fois de requetes ont echouees , latency_ms : temps moy de reponses 
if len(sys.argv) < 2:
    print("Usage: python compute_metrics.py metrics/benchmarks.csv")
    sys.exit(1)

csv_path = sys.argv[1]
df = pd.read_csv(csv_path)

print("--- Résumé métriques ---")
print(df[['recall1','recall3','recall5','mrr']].mean())
print("fallback_rate:", (df['status']!='ok').mean())
print("latency_ms mean:", df['latency_ms'].mean())
