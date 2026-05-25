---
title: Agent Prompt Architect
emoji: ✨
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: src/ui_streamlit.py
pinned: false
---
# Agent-Prompt : Générateur de Prompts Sécurisé (RAG + Fallback)

> Pipeline RAG orchestrant un LLM pour générer des prompts structurés à partir de documentations techniques sur le prompt eengerring (ArXiv, GitHub). Conçu avec une architecture résiliente axée sur la validation des données et la sécurité.

##  À quoi sert ce projet ?
Les LLMs génèrent souvent des prompts vagues ou formatés de manière aléatoire. Ce projet résout ce problème en :
1. Récupérant les meilleures pratiques de Prompt Engineering via recherche vectorielle.
2. Forçant le LLM à générer un prompt structuré (Chain-of-Thought, JSON) basé sur ces pratiques.
3. Bloquant la réponse si elle contient des failles de sécurité (PII), pour basculer sur un système de secours.

---

## Preuves d'Ingénierie & Fonctionnalités

- **Génération sous contrainte (Structured Output) :** Utilisation de l'API Groq (Llama 3.1) en forçant un format de sortie `json_object` strictement validé par Pydantic.
- **Sécurité (Guardrails) :** Validation post-génération par Regex. Le système intercepte et bloque la sortie du LLM si elle hallucine des données sensibles (Cartes bancaires, SSN, emails non anonymisés) ou des tentatives d'injection.
- **Résilience  :** Si le LLM échoue, timeout, ou génère du PII, le système ne crash pas. Il bascule automatiquement sur un mode `fallback_template` déterministe pour garantir une réponse à l'utilisateur.

---

## Évaluation  (Metrics)

Le système d'ingestion (Chunking sémantique) a été évalué sur un *Gold Set* manuel de 20 requêtes catégorisées :

| Métrique | Score | Notes |
| :--- | :--- | :--- |
| **Recall@5** | 0.30 | Identifié : les requêtes courtes (< 5 mots) pénalisent le score. |
| **MRR** | 0.30 | Un reranking par cross-encoder est prévu pour l'optimisation. |
| **Latence Retrieval** | ~180 ms | Temps moyen d'exécution sur le dataset de test. |

*→ Script d'évaluation reproductible : `python scripts/evaluate_recall.py`*



---

## 💻 Stack Technique
- **Orchestration LLM :** API Groq (Llama 3.1)
- **Data & RAG :** ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`)
- **Backend & UI :** Python, FastAPI, Streamlit
- **Qualité :** Validation JSON stricte, Tests unitaires (Pytest)



---
## Limites actuelles : 
Le pipeline intègre des guardrails déterministes (Regex PII, Injection patterns). Cependant, l'architecture actuelle présente des limites documentées :
- **Bypass linguistique (Cross-lingual) :** Les filtres d'injection sont actuellement optimisés pour le français et l'anglais via Regex. Ils sont théoriquement vulnérables à des attaques dans des langues moins représentées dans les patterns de sécurité.
- **Limites des Regex :** Les Regex ne suffisent pas à capturer l'intention malveillante . 
  - *Roadmap :* Transition prévue vers une validation via **"LLM-as-a-Judge"** (un modèle séparé qui valide la sortie du premier) pour une détection sémantique plutôt que lexicale.
## 🚀 Lancer localement

```bash
git clone [https://github.com/nouredine-diallo/Agent-prompt](https://github.com/nouredine-diallo/Agent-prompt)
cd Agent-prompt

# Créer l'environnement et installer les dépendances
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ajouter la clé API Groq
cp .env.example .env 

# Lancer l'API (Terminal 1)
uvicorn src.api:app --reload --port 8000

# Lancer l'interface (Terminal 2)
streamlit run src/ui_streamlit.py

