# Étape 5 — Benchmarks & Évaluation

Tests réalisés sur 20 requêtes pour mesurer la qualité du retrieval et des réponses générées.

## Métriques observées

- Recall@5 : 0.35
- MRR : 0.35
- Latence moyenne : ~2.4s
- Fallback rate : 0%

## Observations

Les requêtes liées au RAG fonctionnent correctement, mais les catégories `security`, `json_format` et certaines requêtes de prompt engineering retournent peu de résultats pertinents.

Après debug :
- le corpus était trop limité
- certaines sources attendues ne correspondaient pas aux fichiers réellement indexés
- plusieurs chunks récupérés étaient trop génériques

## Correctifs appliqués

- normalisation des chemins de sources
- ajout de logs de debug retrieval
- tests avec k=10
- essais de reranking cross-encoder

## Conclusion

Le reranking seul n’améliore pas les résultats : le principal problème vient du corpus et de la couverture documentaire.

Prochaine étape :
- enrichir les documents techniques
- améliorer le chunking
- tester d’autres embeddings 