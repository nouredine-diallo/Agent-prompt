# Étape 5 — Benchmarks & Évaluation

Tests réalisés sur 20 requêtes pour mesurer la qualité du retrieval et des réponses générées.

## Métriques observées

- Recall@5 : 0.35  -> Nouvelles métrics après améliorations : 0.400
- MRR : 0.35  -> Nouvelles métrics après améliorations : 0.327

## Conclusion

Le reranking seul n’améliore pas les résultats : le principal problème vient du corpus et de la couverture documentaire.

Prochaine étape :
- enrichir les documents techniques ( FAIT ET NOUS AVONS OBTENU UNE AMELIORATION DU RECALL ET MRR)
- améliorer le chunking  ( FAIT ET NOUS AVONS OBTENU UNE AMELIORATION DU RECALL ET MRR  )
- tester d’autres embeddings 