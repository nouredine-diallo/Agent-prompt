# GUIDE INGESTION

## Rôle du fichier `src/ingestion.py`
Ce module gère l’ingestion de documents dans ChromaDB : découpe sémantique, normalisation, génération d’identifiants, orchestration de l’embedding, et ajout à la base. Il est crucial pour la qualité du retrieval (Recall/MRR).

## Étapes à réaliser
1. **Lecture et normalisation du texte**
   - Nettoyage, unicité, formatage.
2. **Découpage sémantique**
   - Stratégie basée sur les phrases (phrase-based chunking).
   - Implémenter une règle de chevauchement (overlap) entre les chunks.
3. **Détection automatique de la langue**
   - Pour chaque chunk, détecter la langue (utile pour l’embedder ou le prétraitement).
4. **Génération d’un identifiant unique**
   - Par chunk (ex : hash du contenu + source).
5. **Ajout de métadonnées**
   - Source, date, langue, position, etc.
6. **Orchestration de l’embedding**
   - Appeler le modèle d’embedding sur chaque chunk.
   - Gérer les erreurs ou échecs d’embedding.
7. **Ajout à ChromaDB**
   - Vérifier l’idempotence (ne pas réindexer un chunk déjà présent, via l’id).
   - Sauter les chunks vides ou trop courts.
8. **Logging détaillé**
   - Pour chaque étape (debug, traçabilité).

## Preuves à fournir
- **Tests unitaires** (ex : `tests/test_ingestion.py`) :
  - Vérifier nombre de chunks, chevauchement, ids, détection de langue, etc.
- **Logs d’ingestion** (traçabilité).
- **Commits clairs et documentés**.

## Résumé
Découper, enrichir, embedder et indexer des textes de façon robuste et traçable, en pensant à la qualité du retrieval et à la reproductibilité.