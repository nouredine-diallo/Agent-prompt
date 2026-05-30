Quick Start : Pipeline Meta-Prompting
1. Démarrage Rapide
Bash
# Activer l'environnement virtuel
source .venv/bin/activate
# Faites l ingestion si le dossier chroma_db n'est pas present :
python src/ingestion.py
# Lancer le serveur d'interface
streamlit run src/ui_streamlit.py 

2. Définition de l'Objectif
Pour garantir la qualité de la génération, l'objectif d'entrée doit définir la tâche, le format et le contexte.

Recommandé (Précis) : "Extraire les adresses emails et numéros de téléphone d'un CV au format JSON."

Recommandé (Sécurité) : "Classifier des emails en spam/non-spam avec contraintes de sécurité sur les PII."

À éviter (Vague) : "Faire un résumé avec les données." (Manque de format et de cible).

3. Architecture d'Exécution (4 Phases)
Le pipeline génère le prompt en s'appuyant sur la base vectorielle locale :

Analyse : Extraction sémantique des paramètres de la tâche (format, contraintes de sécurité).

Retrieval (RAG) : Requête sur ChromaDB pour isoler les bonnes pratiques associées à la tâche.

Composition : Assemblage modulaire du prompt (Rôle, Tâche, Format, Few-shot, Sécurité).

Validation : Vérification de l'intégrité de la sortie .

4. Utilisation Programmatique (API interne)
Python
from src.agent import generer_meta_prompt

# Injection de l'objectif métier
objectif = "Extraire les noms de personnes dans un PDF"
prompt = generer_meta_prompt(objectif)

print(prompt)
5. Tests et Validation Automatisés
Pour vérifier l'intégrité de la logique de génération locale avant tout déploiement :