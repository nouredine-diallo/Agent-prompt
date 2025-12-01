# COMPREHENSION.md

## Vue d'ensemble du projet (étapes 0 à 5)

### Objectif général
Construire un pipeline complet d'agent RAG (Retrieval-Augmented Generation) : ingestion de documents, indexation, API, interface utilisateur, benchmarks, et évaluation automatique. Ce type de projet met en avant des compétences d'IA appliquée, d'automatisation, de structuration de données, et de prompt engineering.

---

## Étape 0 : Setup & Préparation
- **Pourquoi ?** Préparer l'environnement pour garantir que tout le monde peut lancer le projet sans erreur.
- **Comment ?**
  - Création de l'arborescence (dossiers/fichiers).
  - Fichier `requirements.txt` : liste les librairies Python nécessaires (ex : fastapi, streamlit, chromadb, sentence-transformers). C'est le développeur qui le crée, en listant ce dont il a besoin pour coder et faire tourner le projet. Il s'appuie sur la doc des librairies, ses recherches, ou des projets similaires.
  - Installation des dépendances : `pip install -r requirements.txt`.
- **Termes à connaître** :
  - **requirements.txt** : fichier texte listant les librairies Python à installer.
  - **venv** : environnement virtuel Python pour isoler les dépendances.

---

## Étape 1 : Ingestion & Indexation
- **Pourquoi ?** Rendre les documents exploitables par l'IA (RAG) : transformer des fichiers (PDF, txt, md) en "chunks" (morceaux) et les indexer pour la recherche.
- **Comment ?**
  - `scripts/fetch_data.py` : télécharge ou prépare les données (docs, articles, etc.).
  - `src/ingestion.py` : découpe les documents en petits morceaux, extrait les mots essentiels, puis transforme chaque chunk en vecteur numérique (embedding) grâce à un modèle de type sentence-transformers. Ces vecteurs sont stockés dans une base (ChromaDB) pour permettre la recherche par similarité.
- **Termes à connaître** :
  - **Chunking** : découpage d'un texte en petits morceaux pour faciliter la recherche.
  - **Embedding** : représentation numérique d'un texte, permettant de comparer la similarité entre textes.
  - **Vector DB** : base de données spécialisée pour stocker et rechercher des vecteurs (ex : ChromaDB).

---

## Étape 2 : API Backend (FastAPI)
- **Pourquoi ?** Permettre à des applications externes (UI, scripts, benchmarks) d'interroger l'agent via une API HTTP.
- **Comment ?**
  - `src/api.py` : expose une route `/generate` qui reçoit une question, interroge la base vectorielle, et retourne une réponse générée + les sources utilisées.
- **Termes à connaître** :
  - **API** : interface permettant à des programmes de communiquer entre eux.
  - **FastAPI** : framework Python pour créer des APIs web rapidement.

---

## Étape 3 : UI Streamlit
- **Pourquoi ?** Offrir une interface simple pour tester l’agent sans coder.
- **Comment ?**
  - `src/ui_streamlit.py` : lance une page web locale où on peut poser des questions à l’agent et voir les réponses/sources.
- **Termes à connaître** :
  - **Streamlit** : framework Python pour créer des interfaces web interactives très rapidement.
  - **UI** : User Interface, interface utilisateur.

---

## Étape 4 : Benchmarks & Évaluation
- **Pourquoi ?** Mesurer la qualité de l’agent (Recall, MRR, latence, fallback) sur des scénarios réels.
- **Comment ?**
  - `scripts/run_benchmarks.py` : envoie des requêtes à l’API avec des questions types, collecte les réponses.
  - `scripts/evaluate_recall.py` : compare les sources retournées avec les sources attendues, calcule Recall@k (taux de bonnes réponses dans le top-k), MRR (Mean Reciprocal Rank), latence, etc.
- **Termes à connaître** :
  - **Recall@k** : % de questions où la bonne source est dans les k premiers résultats.
  - **MRR** : mesure la position de la première bonne réponse (plus c’est haut, mieux c’est).
  - **Fallback** : taux de réponses "je ne sais pas" ou vides.

---

## Étape 5 : Debug, Rerank, Visualisation
- **Pourquoi ?** Comprendre les échecs, améliorer le pipeline, visualiser les résultats.
- **Comment ?**
  - `scripts/debug_retrieval.py` : affiche les chunks réellement retournés pour une question.
  - `scripts/rerank_and_eval.py` : rerank les résultats avec un modèle plus puissant (cross-encoder).
  - `scripts/compute_metrics.py` : génère des graphiques de performance.
- **Termes à connaître** :
  - **Reranker** : modèle qui reclasse les résultats pour améliorer la pertinence.
  - **Cross-encoder** : modèle qui évalue la pertinence d’un couple (question, chunk) plus finement.

---

## Comment utiliser et tester le projet
1. Installer les dépendances : `pip install -r requirements.txt`
2. Ingestion : lancer `src/ingestion.py` pour indexer les documents.
3. Lancer l’API : `uvicorn src.api:app --reload`
4. Tester via l’UI : `streamlit run src/ui_streamlit.py`
5. Lancer les benchmarks : `python3 scripts/run_benchmarks.py`
6. Évaluer : `python3 scripts/evaluate_recall.py`
7. Debug/rerank/visualisation : utiliser les scripts dédiés.

---

## Réponses à tes questions

1. **Qui crée requirements.txt ?**
   - C’est le développeur qui le crée, en listant les librairies nécessaires selon les besoins du projet (doc, expérience, projets similaires).
2. **scripts/fetch_data.py sert à quoi ?**
   - À télécharger ou préparer les données à indexer (pas à "voir" les data, mais à les collecter ou convertir).
3. **src/ingestion.py et les embeddings ?**
   - Oui, il convertit chaque chunk de texte en vecteur numérique (embedding) pour permettre la recherche par similarité.
4. **eval_agent.py fonctionne comment ?**
   - Il envoie des questions à l’agent, compare les réponses/sources retournées avec les attendues, et calcule les métriques (Recall, MRR, etc.).
5. **UI Streamlit, c’est quoi ?**
   - C’est une interface web locale pour tester l’agent sans coder, comme un mini-site web.

---

## Pourquoi ce projet valorise ton CV ?
- Montre ta capacité à concevoir un pipeline IA complet (RAG, ingestion, API, UI, évaluation).
- Démontre des compétences en automatisation, structuration de données, et prompt engineering.
- Prouve que tu sais diagnostiquer, améliorer et documenter un projet IA de bout en bout.
- Met en avant la maîtrise d’outils modernes (FastAPI, Streamlit, ChromaDB, sentence-transformers).
- Illustre ta capacité à itérer, analyser les métriques, et améliorer la qualité d’un agent IA.

---

## Autres points pertinents
- Le projet est modulaire : chaque étape peut être améliorée ou remplacée facilement.
- La logique employée est simple : découper, vectoriser, indexer, interroger, évaluer, améliorer.
- Les termes techniques sont expliqués pour faciliter la prise en main par d’autres prompt engineers ou développeurs.
- Toute la chaîne est automatisée, ce qui est un vrai plus pour l’industrialisation.

---

