# SETUP_REPORT.md

## 1. Vérification de Git
- `git --version` : Succès
- `git init` : Succès

## 2. Vérification de Python & Venv
- `python3 --version` : Succès
- `dpkg -l | grep python3-venv` : Échec (corrigé par installation)
- `sudo apt-get install -y python3-venv` : Succès
- `python3 -m venv .venv` : Succès

## 3. Création de l'Arborescence
- Création des dossiers et fichiers : Succès

## 4. Remplissage des Fichiers de Configuration
- `.gitignore`, `requirements.txt`, `README.md` : Succès

## 5. Installation & Vérification
- `source .venv/bin/activate` : Succès
- `pip install -r requirements.txt` : Échec (timeout réseau, corrigé)
- `sudo apt-get install -y python3-pip` : Succès
- `pip install --default-timeout=300 -r requirements.txt` : Succès
- `python -c "import ..."` : Succès (SETUP: Imports OK)


## 6. Étape 5 : Benchmark RAG End-to-End (2025-10-25)

### Problème rencontré
- Les métriques de retrieval (Recall/MRR) étaient à 0 car les fichiers attendus dans les queries de test (`expected_sources` en .md) ne correspondaient pas aux fichiers réellement indexés (format .txt dans `docs/txt/`).

### Modifications apportées
- Correction automatique du champ `expected_sources` dans `tests/queries_agent_20.jsonl` pour pointer vers les bons fichiers indexés (`docs/txt/xxx.txt`).
- Vérification de la présence des fichiers indexés et adaptation du code d'agent pour normaliser les chemins de sources retournés.
- Ajout de logs de debug pour valider les sources réellement retournées par l'API.
- Relance complète du pipeline de benchmark et d'évaluation.

### Résultat
- La pipeline RAG fonctionne de bout en bout.
- Les métriques de retrieval sont maintenant correctes et non nulles :
	- Recall@1: 1.0 pour les queries RAG, 0.35 globalement
	- MRR: 0.35 globalement
	- Fallback: 0.0
	- Latence moyenne ≈ 2.4s

### Pourquoi ça a fonctionné ?
- Le problème venait d'un simple décalage de format entre les fichiers attendus et ceux indexés. En alignant les `expected_sources` sur le format réel indexé, la comparaison a pu se faire correctement et les métriques sont remontées à des valeurs cohérentes.

-- Tous les prérequis sont installés et vérifiés.
-- L'environnement de développement "agent-prompt" est opérationnel à 100% sur ce workspace (WSL Ubuntu).
