# 🚀 Quick Start: Meta-Prompting Architect

## Utilisation Rapide (2 minutes)

### 1. Lancer l'Interface Web

```bash
cd /home/land/Agent_prompt
source .venv/bin/activate
streamlit run src/ui_streamlit.py --server.port 8501
```

Puis ouvrir: **http://localhost:8501**

### 2. Choisir le Mode

Dans l'interface, tu verras 2 options :

- **💬 Question RAG** : Mode Q&A classique
- **✨ Générer un Prompt** : Mode Meta-Prompting (NOUVEAU)

### 3. Exemples d'Objectifs

#### Extraction
```
Je veux extraire des adresses emails et numéros de téléphone d'un CV
```

#### Classification
```
Classifier des emails en spam/non-spam en JSON avec sécurité
```

#### Résumé
```
Résumer des articles scientifiques en gardant les points clés
```

### 4. Le Prompt est Généré Automatiquement

Le système analyse ton objectif et génère un prompt structuré avec :
- ✅ Rôle adapté
- ✅ Tâche claire
- ✅ Format de sortie (JSON/Liste/Texte)
- ✅ Exemples (few-shot)
- ✅ Contraintes de sécurité

### 5. Télécharger le Prompt

Clique sur **"💾 Télécharger le Prompt"** pour sauvegarder.

---

## Tests Rapides

```bash
# Lancer les tests automatisés
cd /home/land/Agent_prompt
python test_meta_prompting.py
```

Résultat attendu: `🎉 TOUS LES TESTS PASSENT !`

---

## Utilisation Programmatique

```python
from src.agent import generer_meta_prompt

# Générer un prompt
objectif = "Je veux extraire des noms de personnes dans un PDF"
prompt = generer_meta_prompt(objectif)

print(prompt)
```

---

## Architecture Simple

```
Objectif → Analyse → RAG (Techniques) → Composition → Validation → Prompt
```

### Les 4 Phases

1. **COMPRENDRE** : Détecte la tâche, le format, la sécurité
2. **CHERCHER** : RAG pour trouver les bonnes pratiques
3. **COMPOSER** : Assemble le prompt en 5 sections
4. **VALIDER** : Vérifie la cohérence (retry si échec)

---

## Conseils pour de Bons Objectifs

✅ **BON** : "Extraire les adresses emails d'un CV en JSON"
- Spécifique (adresses emails)
- Format clair (JSON)
- Contexte (CV)

❌ **MAUVAIS** : "faire un truc avec des données"
- Trop vague
- Pas de format
- Pas de contexte

---

## FAQ

**Q: Besoin d'une clé OpenAI ?**
R: Non ! Le système utilise des règles simples + RAG (pas de LLM requis)

**Q: Ça marche avec mes documents ?**
R: Oui, tant que tu as indexé des docs dans ChromaDB

**Q: Je peux modifier les templates ?**
R: Oui, modifie les fonctions dans `src/agent.py` (ex: `generer_role()`)

**Q: Combien de temps ça prend ?**
R: ~2 secondes (analyse + RAG + composition)

---

## Fichiers Importants

- `src/agent.py` : Logique de génération (300 lignes)
- `src/ui_streamlit.py` : Interface web (dual mode)
- `test_meta_prompting.py` : Tests automatisés
- `META_PROMPTING_REPORT.md` : Documentation complète

---

## Support

Problème d'import ? Vérifie que tu es bien dans le bon environnement :
```bash
source .venv/bin/activate
which python  # Doit montrer /home/land/.venv/bin/python
```

Tests qui échouent ? Réinstalle les dépendances :
```bash
pip install -r requirements.txt
```

---

**Enjoy ! 🎉**
