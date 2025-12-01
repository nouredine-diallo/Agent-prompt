# VISION CONCEPTUELLE DU PROJET "agent-prompt"

Ceci est votre "Étoile Polaire" conceptuelle. Utilisez ce document pour comprendre le "POURQUOI" de vos tâches.

1. Nom du Projet

Agent-Prompt (Alias: Meta-Prompting Architect / Agent Coach)

2. Mission Principale

Construire un Agent IA Coach capable de générer des prompts de qualité production (optimisés, structurés, sécurisés) pour un objectif donné.

3. L'Utilisateur Cible (Persona)

L'utilisateur est un Ingénieur Prompt (comme vous ou moi). Il ne veut pas d'un jouet. Il veut un outil qui lui fait gagner du temps et lui apprend les meilleures pratiques.

Attentes de l'utilisateur :

"Je veux un prompt qui utilise le CoT, gère les garde-fous de sécurité, et sort un JSON fiable."

"Je veux que le prompt généré soit basé sur la recherche RAG (derniers articles)."

4. Principes de Conception (Le "Quoi")

Le RAG est le Cerveau : La qualité de la base de connaissances (articles de recherche, guides de style) est essentielle. Le RAG doit être utilisé pour justifier les choix de conception du prompt généré.

Le Meta-Prompting est la Compétence : Le cœur du projet est l'Agent qui planifie (CoT interne) la création du prompt final. Il n'improvise pas ; il conçoit.

La Validation est la Sécurité : Le prompt généré doit être auto-documenté (expliquer pourquoi il est structuré ainsi) et robuste (inclure des instructions de formatage et de sécurité).

La Qualité > Vitesse : Il vaut mieux prendre 10 secondes pour générer un prompt parfait que 2 secondes pour un prompt médiocre.

5. Fonctionnalités Clés (MVP)

Ingestion RAG : Indexer des PDF/MD de recherche sur le Prompt Engineering.

Orchestration d'Agent : L'Agent doit utiliser le RAG (Tool Use) pour informer sa décision.

Génération Structurée : L'Agent génère le prompt final.

Interface Simple (Streamlit) : Une UI pour entrer l'objectif et recevoir le prompt.
