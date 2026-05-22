# Étape 1 — Data sourcing & ingestion RAG

## Statut
Terminé.

## Travail réalisé

- Extraction et nettoyage des fichier des  sources techniques (PDF, GitHub, documentation).
- Création du pipeline d’ingestion vers ChromaDB.
- Chunking sémantique avec overlap.
- Génération des embeddings et indexation des chunks.
- Mise en place d’un premier test de retrieval. 

## Résultats actuels

- 44 fichiers indexés
- 1735 chunks après déduplication
- Recall@5 : 0.40
- MRR : 0.32 

## Limites identifiées

- Certaines URLs étaient invalides ou protégées (403/404).
- Le chunking actuel reste améliorable pour les requêtes courtes.
- Le reranking n’est pas encore implémenté.  

## Notes

Les logs complets et scripts intermédiaires utilisés pendant le développement ont été conservés dans ce dossier à titre de référence technique. 