---
title: Agent Prompt Architect
emoji: ✨
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: src/ui_streamlit.py
pinned: false
---
# Agent-Prompt : Générateur de Prompts Sécurisé RAG 

> Pipeline RAG utilisant  un LLM pour générer des prompts structurés à partir de documentations techniques sur le prompt eengerring (ArXiv, GitHub). 

##  À quoi sert ce projet ?
Les LLMs génèrent souvent des prompts vagues ou  de manière aléatoire. Ce projet résout ce problème en :
1. Récupérant les meilleures pratiques de Prompt Engineering via recherche vectorielle.
2. Forçant le LLM à générer un prompt structuré  basé sur ces pratiques( structuré , limitant les hallucination , mettre en place des procédures de sécurités ...)

---
* [Tester la Démo Live sur Hugging Face Spaces](https://huggingface.co/spaces/Land248/Agent-prompt)**

*(Note : Si l'application affiche une erreur de quota API Groq, vous pouvez entrer votre propre clé API dans le menu de l'application pour la tester en illimité).*

--- 
---

## Démonstration 

[[Demo](https://github.com/user-attachments/assets/e476c117-6402-4539-8faa-aad20c8ff8f5)]

*Le pipeline extrait les bonnes pratiques depuis ChromaDB(RAG), construit la structure, vérifie la sécurité (Guardrails), et force une sortie JSON via Llama 3.1.*

---

## Fonctionnalités
- **Structured Output  :** Utilisation de l'API Groq (Llama 3.1) avec une validation stricte du format JSON via **Pydantic V** (`model_validate_json`).
- **Guardrails  :** Validation post-génération par Regex . Le systeme bloque la génération du LLM si il y a des données sensible non autorisées (Cartes bancaires, SSN).
- **Fallback:** Si le LLM échoue, timeout, ou génère du PII, le système ne crash pas. Il bascule automatiquement sur un mode `fallback_template` déterministe pour garantir la continuité de service.

---

## Évaluation-Metrics

Le système d'ingestion (Chunking sémantique) a été évalué sur un *Gold Set* manuel de 20 requêtes catégorisées :

| Métrique | Score | Notes |
| :--- | :--- | :--- |
| **Recall@5** | 0.400 | Identifié : les requêtes courtes (< 5 mots) pénalisent le score. |
| **MRR** | 0.327 |  |
| **Latence Retrieval** | ~180 ms | Temps moyen d'exécution sur le dataset de test. |

*→ Script d'évaluation reproductible : `python scripts/evaluate_recall.py`*



---

## Stack Technique
- **Orchestration LLM :** API Groq (Llama 3.1)
- **Data & RAG :** ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`)
- **Backend & UI :** Python, FastAPI, Streamlit
- **Qualité :** Validation JSON stricte, Tests unitaires (Pytest)



---
## Limites Actuelles & Sécurité

- **Bypass linguistique :** Les filtres sont actuellement optimisés via Regex. Ils sont vulnérables à des bypass sémantiques ou multilingues.
- **Limites des Regex :** Les Regex ne suffisent pas à capturer l'intention malveillante (ex: Prompt Injection en entrée). 
  - *Roadmap Sécurité :* Transition possible/prévue vers l'intégration d'un  **"LLM-as-a-Judge"**  pour une détection sémantique complète.
 
## Ameliorations & Peer Review

Suite à une revue de code externe par des développeurs Data/Backend seniors, le score de base actuel de la DB vectorielle (Recall@5 = 0.400) a mis en évidence des axes d'amélioration critiques . Voici les ameliorations proposées : 

1. **[Embedding] Barrière de la langue :** Remplacement de `all-MiniLM-L6-v2` par un modèle d'embedding multilingue (ex: `paraphrase-multilingual-MiniLM`) pour mieux capturer la sémantique francophone.
2. **[Retrieval] Lost in the Middle :**placer les informations les plus pertinentes aux extrémités du prompt ainsi on évite le bruit .
3. **[Orchestration] Transition vers ReAct :** Évolution du pipeline linéaire actuel vers une véritable boucle Agentique (ReAct) permettant au LLM d'invoquer l'outil de recherche ChromaDB de manière autonome.
## Lancer localement

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

