# Étape 4 — API & Interface

Ajout d’une API FastAPI et d’une interface Streamlit pour tester le pipeline RAG localement avec Ollama.

## Ce qui a été mis en place

- API FastAPI (`/generate`)
- Interface Streamlit pour tester les requêtes
- Intégration locale via Ollama
- Validation JSON des réponses
- Logs simples pour debug et smoke tests

## Tests réalisés

- Vérification du endpoint `/`
- Génération de réponses via `/generate`
- Test UI → requête → affichage réponse
- Vérification des erreurs dans les logs

## Points à améliorer

- Ajouter authentification et rate limiting
- Réduire la latence des réponses
- Ajouter Docker et CI
- Améliorer le monitoring des erreurs