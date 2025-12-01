# 🤖 Agent-Prompt : Meta-Prompting RAG Architect

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-3%2F3%20passing-brightgreen.svg)](test_meta_prompting.py)
[![Code Quality](https://img.shields.io/badge/Quality-Production-success.svg)](ARCHITECTURE_PROJET.md)

Agent RAG (Retrieval-Augmented Generation) capable de générer des prompts optimisés via un pipeline Meta-Prompting en 4 phases, avec validation sécurité et base de connaissances (ArXiv, guides, GitHub).

## ✨ Fonctionnalités

### 🎯 Meta-Prompting (4 phases)
1. **Parse** : Extraction automatique de l'objectif utilisateur
2. **Fetch** : Récupération contexte pertinent via RAG (ChromaDB)
3. **Build** : Construction prompt structuré (CoT + JSON schema + guardrails)
4. **Validate** : Validation sécurité (PII, injection, format)

### 🔒 Validation Sécurité
- ✅ Détection PII (emails, SSN, cartes crédit)
- ✅ Détection injection de prompt
- ✅ Validation schéma JSON strict

### 📊 RAG Pipeline
- **1735 chunks** indexés depuis 44 sources (ArXiv, GitHub, guides)
- **Chunking sémantique** (200 mots, overlap 50)
- **Embeddings** : SentenceTransformer `all-MiniLM-L6-v2`
- **Base vectorielle** : ChromaDB persistant

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/nouredine-diallo/Agent-Prompt.git
cd Agent-Prompt
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Indexation (première fois uniquement)
```bash
python src/ingestion.py
# → Crée chroma_db/ avec 1735 chunks
```

### Lancement

#### Option 1 : Interface Streamlit
```bash
# Terminal 1 : API
uvicorn src.api:app --reload --port 8000

# Terminal 2 : UI
streamlit run src/ui_streamlit.py
# → Ouvrir http://localhost:8501
```

#### Option 2 : Test direct
```bash
python test_meta_prompting.py
# ✅ Test extraction email : OK
# ✅ Test sécurité : OK
# ✅ Test classification JSON : OK
```

#### Option 3 : Utilisation programmatique
```python
from src.agent import generer_meta_prompt

# Génération automatique de prompt
prompt = generer_meta_prompt("Crée un classificateur de sentiment")
print(prompt)
# → Retourne prompt optimisé avec CoT + JSON schema + exemples
```

## 📁 Architecture

```
Agent-Prompt/
├── src/
│   ├── agent.py              # ⭐ RAG + Meta-Prompting (4 phases)
│   ├── ingestion.py          # Chunking + Embedding + ChromaDB
│   ├── validator.py          # Validation PII/Injection/JSON
│   ├── api.py                # FastAPI (expose /generate)
│   ├── ui_streamlit.py       # Interface chat
│   ├── prompts/
│   │   └── meta_architect_prompt.py  # System prompt CoT
│   └── agent/
│       └── orchestrator.py   # Orchestration avec fallback
├── tests/
│   └── queries_agent_20.jsonl  # Gold set RAG (20 queries)
├── test_meta_prompting.py    # Tests fonctionnels (3/3 ✅)
├── docs/txt/                 # 44 fichiers sources
└── chroma_db/                # Base vectorielle (1735 chunks)
```

Voir [ARCHITECTURE_PROJET.md](ARCHITECTURE_PROJET.md) pour détails complets.

## 🧪 Tests

```bash
# Tests fonctionnels meta-prompting
python test_meta_prompting.py

# Tests RAG (Recall@5, MRR)
python scripts/evaluate_recall.py
```

**Résultats actuels :**
- ✅ Tests meta-prompting : 3/3 passants
- ⚠️ Recall@5 : 0.40 (objectif: 0.60)
- ⚠️ MRR : 0.32 (objectif: 0.50)

## 📊 Métriques

| Métrique | Valeur | Statut |
|----------|--------|--------|
| Fichiers sources | 44 | ✅ |
| Chunks indexés | 1735 | ✅ |
| Tests passants | 3/3 | ✅ |
| Validation sécurité | PII + Injection | ✅ |

## 🛠️ Stack Technique

- **Python 3.10+**
- **FastAPI** : API REST
- **Streamlit** : Interface utilisateur
- **ChromaDB** : Base vectorielle
- **SentenceTransformers** : Embeddings
- **LangChain** : Orchestration (optionnel, avec fallback)
- **Pytest** : Tests unitaires

## 📖 Documentation

- [ARCHITECTURE_PROJET.md](ARCHITECTURE_PROJET.md) : Architecture complète 4 couches
- [QUICK_START_META_PROMPTING.md](QUICK_START_META_PROMPTING.md) : Guide utilisateur
- [docs/AGENT_RULES.md](docs/AGENT_RULES.md) : Règles métier agent
- [docs/PROJECT_VISION.md](docs/PROJECT_VISION.md) : Vision projet

## 🎓 Différenciateurs

1. **Meta-Prompting 4-phases** : Pipeline structuré Parse→Fetch→Build→Validate
2. **Orchestration robuste** : Fallback gracieux si dépendances manquantes
3. **Qualité industrielle** : Validation PII, détection injection, tests automatisés
4. **Code maintenable** : Architecture claire et documentée
5. **Localisation française** : Commentaires et documentation en français

## 🔥 Roadmap

- [ ] Améliorer Recall@5 (0.40 → 0.60) via reranking
- [ ] Ajouter détection toxicité (actuellement stub)
- [ ] Dashboard métriques (Grafana/Streamlit)
- [ ] Déploiement Docker + API publique

## 📜 Licence

MIT License - Voir [LICENSE](LICENSE) pour détails.

## 👤 Auteur

**Nouredine Diallo**
- GitHub: [@nouredine-diallo](https://github.com/nouredine-diallo)

---

⭐ Si ce projet vous aide, n'hésitez pas à laisser une étoile!
