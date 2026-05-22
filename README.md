# Agent-Prompt — Pipeline RAG avec Meta-Prompting

> Pipeline RAG utilisé pour générer des prompts structurés à partir de sources techniques (GitHub, ArXiv, documentation). 
> Évalué quantitativement avec Ragas (faithfulness, relevancy) et métriques custom (Recall@5, MRR).

---

## 📊 Métriques d'évaluation (Ragas — 2026)

| Métrique          | Score | Cible  | Statut |
|-------------------|-------|--------|--------|
| Faithfulness      | À MESURER | > 0.80 | 🟡 |
| Answer Relevancy  | À MESURER | > 0.75 | 🟡 |
| Recall@5 (custom) | 0.40  | 0.60   | 🔴 |
| MRR (custom)      | 0.32  | 0.50   | 🔴 |

*→ Reproduire l'évaluation : `python scripts/evaluate_ragas.py`*
*→ Dataset utilisé : 20 requêtes annotées (`data/queries_agent_20.jsonl`)*

---

## Architecture

Le pipeline récupère d'abord les meilleures pratiques depuis ArXiv, GitHub et des guides techniques, puis les utilise comme contexte pour générer des prompts validés et sécurisés.

1. **Ingestion :** Chunking sémantique avec overlap 50 mots, détection de langue.
2. **Retrieval :** Embedding + recherche vectorielle ChromaDB.
3. **Meta-Prompting :** 4 phases de génération structurée.
4. **Validation :** `validator.py` vérifie l'absence de PII, d'injection de prompt et la conformité du schéma JSON.

---

## Lancer localement

```bash
git clone https://github.com/nouredine-diallo/Agent-prompt
cd Agent-prompt
pip install -r requirements.txt
cp .env.example .env    # Ajouter la clé API OpenAI/Vertex

# Ingestion de la base de connaissances
python src/ingestion.py

# Lancement de l'interface
streamlit run ui_streamlit.py
```

---

## Limites connues & Tradeoffs

**Recall@5 = 0.40 (cible 0.60) :** La stratégie de chunking actuelle n'est pas optimale pour les requêtes courtes. L'ajout d'un reranking par cross-encoder est nécessaire.

**MRR = 0.32 :** Le système peine à remonter la meilleure source en position 1.

**Performances :** L'absence de cache des requêtes entraîne des appels API redondants.

## Roadmap

- [ ] Cross-encoder reranking pour améliorer le Recall@5.
- [ ] Implémentation d'un cache mémoire.
