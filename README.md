---
title: Agent Prompt Architect
emoji: ✨
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: src/ui_streamlit.py
pinned: false
---
# Agent-Prompt : Générateur de Prompts Sécurisé venant d'un RAG 

Pipeline orienté Data/Backend permettant de générer des System Prompts stricts et sécurisés pour l'extraction de données, basés sur les pratiques de Prompt Engineering (ArXiv, GitHub).

Le problème : Les LLMs hallucine ,respectent pas forcément les consignes ...
La solution : Un outil qui force le LLM à respecter un certain schema  strict via RAG, Pydantic et Guardrails. 

---
* [Tester la Démo Live sur Hugging Face Spaces](https://huggingface.co/spaces/Land248/Agent-prompt)**

*(Note : Si l'application affiche une erreur de quota API Groq, vous pouvez entrer votre propre clé API dans le menu de l'application pour la tester en illimité).*

--- 


## Fonctionnalités
- **Structured Output  :** Validation stricte des entrées/sorties avec Pydantic (model_validate_json). 
- **Guardrails  :**Le système bloque la sortie si des données sensibles non autorisées (Cartes bancaires, SSN) sont générées ->utilisation du fallback
- **Fallback:** Si le LLM échoue, timeout, ou génère du PII, le système ne crash pas. Il switch automatiquement sur un mode `fallback_template` 

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
- **LLM :** API Groq (Llama 3.1)
- **Data & RAG :** ChromaDB, SentenceTransformers (`all-MiniLM-L6-v2`)
- **Backend & UI :** Python, FastAPI, Streamlit
- **Qualité :** Validation JSON stricte, Tests unitaires (Pytest)



---
## Limites Actuelles & Sécurité

- **Bypass linguistique :** Les filtres sont verifier grace a Regex . Mais ils sont vulnérables à des bypass sémantiques ou multilingues.
- **Limites des Regex :** Les Regex ne suffisent pas à capturer l'intention malveillante (ex: Prompt Injection en entrée). 
  - *Roadmap Sécurité :* Transition possible/prévue vers l'intégration d'un  **"LLM-as-a-Judge"**  pour une détection sémantique complète.
 
## Ameliorations & Avis de dev 

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

