#!/bin/bash
# Runner ETAPE 5 — mode réel
set -e

API_URL="http://127.0.0.1:8000"
LOG_API="logs/step4_api.log"
LOG_RUN="logs/step5_run_real.log"
QUERIES="tests/queries_agent_20.jsonl"
METRICS="metrics/benchmarks.csv"

# 1. Lancer l'API (prod-like, sans reload)
source .venv/bin/activate
nohup uvicorn src.api:app --host 127.0.0.1 --port 8000 --workers 1 > "$LOG_API" 2>&1 &
API_PID=$!

# 2. Attendre que l'API soit prête (endpoint /healthz ou /)
echo "[Runner] Attente de l'API..."
for i in {1..30}; do
  if curl -sSf "$API_URL/" >/dev/null 2>&1; then
    echo "[Runner] API ready."
    break
  fi
  echo "[Runner] waiting for API... ($i)"
  sleep 1
done

# 3. Lancer le benchmark en mode réel (mock désactivé)
# (Adapter la ligne suivante si tu as un script d'intégration plus avancé)
python3 scripts/run_benchmarks.py --use-mock false 2>&1 | tee "$LOG_RUN"

# 4. (Optionnel) Évaluer Recall/MRR si evaluate_recall.py existe
if [ -f scripts/evaluate_recall.py ]; then
  python3 scripts/evaluate_recall.py --results "$LOG_RUN" --queries "$QUERIES" --k 5 | tee logs/eval_step5_real.log
fi

# 5. (Optionnel) Générer rapport final
if [ -f scripts/generate_etape5_report.py ]; then
  python3 scripts/generate_etape5_report.py | tee logs/generate_report_step5.log
fi

# 6. Arrêter l'API
kill $API_PID
