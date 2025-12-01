# DIRECTIVES TECHNIQUES OBLIGATOIRES POUR L'AGENT "agent-prompt"

Ceci est votre ensemble de règles non négociables. Référez-vous à ce document pour toute tâche de génération ou de modification de code.

1. Stack Technique (Strict)

Langage : Python 3.11+

Orchestration : LangChain (ou LlamaIndex si spécifié)

Vector DB : ChromaDB (local)

Embeddings : sentence-transformers (modèle all-MiniLM-L6-v2)

API : FastAPI

UI : Streamlit

Tests : Pytest

Dépendances : Gérées via requirements.txt

Règle : Ne pas introduire de nouvelles dépendances majeures sans validation.

2. Qualité du Code (Clean Code)

Typage Statique : Tout le code Python DOIT utiliser les "Type Hints" (ex: def ma_fonction(nom: str) -> bool:). C'est crucial pour votre propre compréhension.

Docstrings : Toute fonction ou classe non triviale DOIT avoir une docstring (format Google ou reST).

Formatage : Utiliser black et isort pour le formatage (ou s'y conformer).

Clarté : Préférer un code lisible et explicite à un code "intelligent" et court.

3. Sécurité & Robustesse (Non Négociable)

API Keys : AUCUNE clé API ne doit être en dur dans le code. Utiliser python-dotenv et charger les clés depuis un fichier .env (qui est dans .gitignore).

Gestion des Erreurs : Tous les appels API externes (LLM) et les opérations I/O (lecture de fichiers, écriture DB) DOIVENT être encapsulés dans des blocs try...except robustes.

Validation d'Entrée : Utiliser jsonschema pour valider les sorties JSON du LLM (ne jamais faire confiance au LLM). Utiliser Pydantic (via FastAPI) pour valider les entrées API.

4. Tests (Obligatoires)

Couverture : Toute nouvelle fonction logique dans agent.py, validator.py ou ingestion.py DOIT être accompagnée d'un test unitaire dans tests/.

Workflow : Avant de soumettre une modification, exécutez toujours pytest -q. Si les tests échouent, corrigez AVANT de continuer.

5. Environnement

Activation : Toujours supposer que vous travaillez dans l'environnement virtuel .venv.
