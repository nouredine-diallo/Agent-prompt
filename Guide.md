Quick Start : Pipeline Meta-Prompting
1. Démarrage Rapide
Bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer le serveur d'interface
streamlit run src/ui_streamlit.py --server.port 8501
L'interface est accessible via http://localhost:8501.

2. Modes d'Exécution (Interface)
L'application expose deux pipelines distincts :

Mode RAG Standard : Système de Question-Réponse sourcé.

Mode Meta-Prompting : Génération déterministe de prompts structurés.

3. Définition de l'Objectif
Pour garantir la qualité de la génération, l'objectif d'entrée doit définir la tâche, le format et le contexte.

Recommandé (Précis) : "Extraire les adresses emails et numéros de téléphone d'un CV au format JSON."

Recommandé (Sécurité) : "Classifier des emails en spam/non-spam avec contraintes de sécurité sur les PII."

À éviter (Vague) : "Faire un résumé avec les données." (Manque de format et de cible).

4. Architecture d'Exécution (4 Phases)
Le pipeline génère le prompt en s'appuyant sur la base vectorielle locale :

Analyse : Extraction sémantique des paramètres de la tâche (format, contraintes de sécurité).

Retrieval (RAG) : Requête sur ChromaDB pour isoler les bonnes pratiques associées à la tâche.

Composition : Assemblage modulaire du prompt (Rôle, Tâche, Format, Few-shot, Sécurité).

Validation : Vérification de l'intégrité de la sortie (mécanisme de retry automatique).

5. Utilisation Programmatique (API interne)
Python
from src.agent import generer_meta_prompt

# Injection de l'objectif métier
objectif = "Extraire les noms de personnes dans un PDF"
prompt = generer_meta_prompt(objectif)

print(prompt)
6. Tests et Validation Automatisés
Pour vérifier l'intégrité de la logique de génération locale avant tout déploiement :

Bash
python test_meta_prompting.py
7. Résolution des Problèmes (Troubleshooting)
Base de connaissances vide : Le RAG nécessite l'ingestion préalable de documents dans l'instance ChromaDB.

Erreur d'environnement : Vérifiez l'activation de l'environnement virtuel (which python doit pointer vers .venv).

Configuration des heuristiques : Les templates de composition modulaires sont éditables directement dans src/agent.py.