# ETAPE 4 — API & UI de Production : Rapport Final

## 1. Objectif
Exposer l'agent RAG comme une API FastAPI robuste et une interface utilisateur Streamlit, prêtes pour la production, avec instructions de lancement et vérifications.

---

## 2. Fichiers Clés
- **Backend API** : `src/api.py` (FastAPI, endpoints `/generate` et `/`)
- **Frontend UI** : `src/ui_streamlit.py` (Streamlit, chat interactif)
- **Dépendances** : `requirements.txt` (toutes librairies nécessaires)

---

## 3. Instructions de Lancement

### 3.1. Installation des dépendances
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2. Configuration de l'environnement
Créez un fichier `.env` à la racine avec votre clé OpenAI :
```
OPENAI_API_KEY=sk-...
```

### 3.3. Lancer l'API Backend (FastAPI)
```bash
source .venv/bin/activate
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```
- Accès API : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3.4. Lancer l'UI Frontend (Streamlit)
Dans un **autre terminal** :
```bash
source .venv/bin/activate
streamlit run src/ui_streamlit.py
```
- Accès UI : [http://localhost:8501](http://localhost:8501)

---


## 4. Vérifications (Smoke Check)

### 4.1. Lancer l'API FastAPI (terminal A)
```bash
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

### 4.2. Vérifier endpoint racine
```bash
curl -sS http://127.0.0.1:8000/ | sed -n '1,40p'
```
**Exemple de sortie :**
```
{"status":"Agent-Prompt API is running"}
```

### 4.3. Tester /generate en mode factice
```bash
curl -sS -X POST "http://127.0.0.1:8000/generate" \
	-H "Content-Type: application/json" \
	-d '{"query":"Quelles sont les bonnes pratiques de prompt engineering ?","mock":true}' | jq '.' | sed -n '1,80p'
```
**Exemple de sortie :**
```
{
	"answer": "Réponse factice (mock) pour: Quelles sont les bonnes pratiques de prompt engineering ?",
	"sources": [],
	"metadata": {
		"query_id": "...",
		"mock": true,
		"failure_reason": "ok"
	}
}
```

### 4.4. Lancer l’UI Streamlit (terminal B)
```bash
streamlit run src/ui_streamlit.py
```
Ouvrir http://localhost:8501 et vérifier :
- L’UI charge, tu peux envoyer une requête, résultat affiché.

### 4.5. Vérifier logs d’erreur (si logs/step4_api.log ou step4_ui.log existent)
```bash
tail -n 200 logs/step4_api.log
tail -n 200 logs/step4_ui.log
```

### 4.6. Critères de succès immédiats
- API / répond HTTP 200.
- /generate retourne JSON valide (schéma minimal : answer string, sources array).
- UI se lance, envoie requête et affiche réponse.
- Pas d’exceptions non gérées dans les logs.

**Attention :**
- Pour un fonctionnement complet, créez un fichier `.env` à la racine avec :
		```
		OPENAI_API_KEY=sk-...
		```
- La logique agent réelle doit remplacer la fonction factice dans `src/agent.py`.

---

---

## 5. Dépendances Principales
- fastapi, uvicorn[standard], streamlit, requests, python-dotenv, openai, langchain, chromadb, sentence-transformers, jsonschema, pytest

---

## 6. Recommandations pour la production

**Priorité haute (avant déploiement public)**
- Authentification / Rate limiting pour /generate (API key, JWT ou API gateway).
- Désactiver --reload et lancer uvicorn avec plusieurs workers (Gunicorn + Uvicorn workers).
- Sécuriser la clé : ne pas stocker clé en clair ; utiliser secret manager / vault / env vars via service.
- Logs structurés (JSON), centralisation (file + stdout) et rotation (logrotate).
- Timeouts & retries configurés pour appels LLM et retrieval.
- Validation d’input (pydantic models) pour /generate (déjà en place).
- Tests automatisés : pytest tests for API endpoints (happy path + error cases).
- Dockerfile + Compose pour packaging local / CI.
- Health check endpoints (/healthz, /ready) pour orchestration.
- Monitoring / metrics (Prometheus endpoints, request latency histograms).

**Priorité moyenne**
- TLS termination (via reverse proxy NGINX/Cloud), caching responses fréquentes, circuit breaker.
- Rate-limits par IP et per-user.
- CI pipeline (GitHub Actions) : tests, lint, build image.

---

**Fin de l'étape 4 : API & UI prêtes à l'emploi.**
