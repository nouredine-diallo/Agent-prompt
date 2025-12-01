
import os
import json
import re
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

MODEL = "all-MiniLM-L6-v2"
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

def generate_with_checks(query_text, query_id=None, k=5):
	"""RAG pipeline: embed query, search ChromaDB, return chunks"""
	try:
		model = SentenceTransformer(MODEL)
		client = chromadb.PersistentClient(path=DB_DIR)
		col = client.get_or_create_collection("docs")
		
		q_emb = model.encode([query_text], convert_to_numpy=True)
		res = col.query(
			query_embeddings=q_emb.tolist(),
			n_results=k,
			include=["documents", "metadatas", "distances"]
		)
		
		answers = res.get("documents", [[]])[0]
		metas = res.get("metadatas", [[]])[0]
		
		# Normaliser les chemins source
		def norm_src(m):
			src = m.get("source") or m.get("title")
			if src:
				rel = os.path.relpath(src, os.path.dirname(os.path.dirname(__file__)))
				return rel.replace('\\', '/')
			return ""
		
		sources = [norm_src(m) for m in metas]
		answer = "\n---\n".join(answers[:k]) if answers else "No results found"
		
		print(f"[{query_id[:8] if query_id else 'N/A'}] sources: {len(sources)}")  # oops debug left in
		
		return {
			"answer": answer,
			"sources": sources,
			"metadata": {"query_id": query_id, "failure_reason": "ok"}
		}
	
	except Exception as e:
		return {
			"answer": "",
			"sources": [],
			"metadata": {"query_id": query_id, "failure_reason": str(e)}
		}


# ============================================================================
# META-PROMPTING - Générer des prompts optimisés depuis des objectifs
# ============================================================================

def _parse_goal(goal: str):
	"""Quick & dirty parser - détecte task type, format, security flags"""
	txt = goal.lower()
	
	# Détection tâche - matching simple par mots-clés
	task = "general"
	if any(w in txt for w in ["extraire", "extraction", "extract", "récupérer"]):
		task = "extraction"
	elif any(w in txt for w in ["classifier", "classification", "catégoris"]):
		task = "classification"
	elif any(w in txt for w in ["résumer", "résumé", "summary", "synthèse"]):
		task = "résumé"
	elif any(w in txt for w in ["valider", "validation", "vérifier"]):
		task = "validation"
	
	# Format - default to json for structured tasks
	fmt = "json" if task in ["extraction", "classification"] else "texte"
	if " json" in txt or "en json" in txt or "format json" in txt:
		fmt = "json"
	elif any(w in txt for w in ["en liste", "liste", "bullet"]):
		fmt = "liste"
	elif any(w in txt for w in ["en texte", "texte brut", "paragraphe", "format texte"]):
		fmt = "texte"  # override explicite
	
	# Security keywords
	needs_security = any(w in txt for w in [
		"sécurité", "securite", "security", "confidentiel", 
		"privé", "protection", "guardrail", "safe", "rgpd"
	])
	
	# Extraire données cible (découpage hacky)
	target = goal
	for keyword in ["extraire", "classifier", "résumer", "valider"]:
		if keyword in txt:
			parts = txt.split(keyword, 1)
			if len(parts) > 1:
				# Grab first few words after the verb
				target = " ".join(parts[1].strip().split()[:5])
				break
	
	print(f"DEBUG parsed goal: task={task}, fmt={fmt}, security={needs_security}")  # oops forgot to remove this
	
	return {
		"task": task,
		"format": fmt,
		"security": needs_security,
		"target": target
	}


def _build_prompt(ctx: dict, rag_chunks: list = None) -> str:
	"""Assemble le prompt final - template-based approach"""
	
	# Mapping rôle (simple dict lookup)
	roles = {
		"extraction": "Tu es un assistant expert en extraction de données structurées.",
		"classification": "Tu es un expert en classification et catégorisation de texte.",
		"résumé": "Tu es un assistant spécialisé en résumé et synthèse de documents.",
		"validation": "Tu es un expert en validation et vérification de données.",
	}
	role = roles.get(ctx['task'], "Tu es un assistant IA professionnel et précis.")
	
	# Description de la tâche
	if ctx['task'] == 'extraction':
		task_desc = f"Extrais {ctx['target']} du texte fourni."
	elif ctx['task'] == "classification":
		task_desc = f"Classifie le texte selon {ctx['target']}."
	elif ctx['task'] == "résumé":
		task_desc = f"Résume le texte en te concentrant sur {ctx['target']}."
	else:
		task_desc = f"Réalise la tâche suivante : {ctx['target']}"
	
	# Spécification du format
	if ctx['format'] == 'json':
		# TODO: vérifier si RAG chunks ont de meilleurs exemples de schéma
		json_schema = """Retourne un JSON avec cette structure :
{
  "resultat": [...],
  "confiance": 0.0-1.0,
  "source": "..."
}"""
		# Petit hack: essayer d'extraire un schéma depuis RAG si dispo
		if rag_chunks:
			for chunk in rag_chunks:
				if "JSON" in chunk and "schema" in chunk.lower():
					json_schema = chunk[:500]  # prendre les 500 premiers caractères
					break
		format_spec = json_schema
	elif ctx['format'] == 'liste':
		format_spec = "Retourne ta réponse sous forme de liste à puces (bullet points)."
	else:
		format_spec = "Retourne ta réponse en texte clair et structuré."
	
	# Exemples (few-shot)
	examples = []
	if rag_chunks:
		for chunk in rag_chunks:
			if "example" in chunk.lower() or "exemple" in chunk.lower():
				examples.append(chunk[:200])
				if len(examples) >= 2:  # max 2 exemples
					break
	
	if not examples and ctx['task'] == "extraction" and ctx['format'] == 'json':
		# Fallback hardcoded examples
		examples = ["""Exemple 1:
Input: "Contact: jean@example.com"
Output: {"email": "jean@example.com", "confiance": 0.95}

Exemple 2:
Input: "Email: marie.dupont@test.fr"
Output: {"email": "marie.dupont@test.fr", "confiance": 0.98}"""]
	
	examples_text = "\n\n".join(examples) if examples else f"[Fournis 2-3 exemples concrets pour: {ctx['task']}]"
	
	# Constraints
	constraints = ["- Vérifie la validité du format avant de retourner",
	               "- Indique ton niveau de confiance dans la réponse"]
	
	if ctx.get('security'):
		constraints.insert(0, "- Ne jamais partager d'informations personnelles sensibles")
		constraints.insert(1, "- Anonymiser les données si nécessaire")
		constraints.insert(2, "- Respecter le RGPD et la confidentialité")
	
	# Optionnel: récupérer contraintes du RAG (approche fainéante - juste le premier chunk)
	if rag_chunks:
		for chunk in rag_chunks:
			if any(w in chunk.lower() for w in ["contrainte", "règle", "attention", "important"]):
				constraints.append(f"- {chunk[:100]}")
				break
	
	constraints_text = "\n".join(constraints)
	
	# Template assembly
	prompt = f"""=== RÔLE ===
{role}

=== TÂCHE ===
{task_desc}

=== FORMAT DE SORTIE ===
{format_spec}

=== EXEMPLES ===
{examples_text}

=== CONTRAINTES ===
{constraints_text}

=== INSTRUCTIONS FINALES ===
Maintenant, applique ce prompt au texte que l'utilisateur va te fournir.
Suis scrupuleusement le format de sortie et les contraintes ci-dessus.
"""
	
	# Validation rapide inline (pas besoin de fonction séparée)
	missing = []
	if "RÔLE" not in prompt:
		missing.append("role")
	if "TÂCHE" not in prompt:
		missing.append("task")
	if ctx['format'] == 'json' and 'JSON' not in prompt and 'json' not in prompt:
		missing.append("json_format")
	if ctx.get('security') and not any(w in prompt.lower() for w in ['sécurité', 'confidentiel', 'rgpd']):
		missing.append("security_guardrails")
	
	if missing:
		print(f"[WARNING] Prompt missing: {missing}")  # log mais pas d'échec
	
	return prompt


def generer_meta_prompt(goal: str, max_retries: int = 2) -> str:
	"""
	Main entry point - generates optimized prompt from user goal
	
	Works by: parse goal → fetch RAG examples → build template → return
	"""
	ctx = _parse_goal(goal)
	print(f"[Meta-Prompt] Context: task={ctx['task']}, format={ctx['format']}")
	
	# Récupérer chunks RAG pour exemples/techniques
	rag_chunks = []
	try:
		model = SentenceTransformer(MODEL)
		client = chromadb.PersistentClient(path=DB_DIR)
		coll = client.get_or_create_collection("docs")
		
		# Construire requêtes selon contexte
		queries = [
			f"techniques de prompt pour {ctx['task']}",
			f"structurer un prompt pour {ctx['format']}",
		]
		if ctx.get('security'):
			queries.append("guardrails de sécurité dans les prompts")
		
		for q in queries:
			emb = model.encode([q], convert_to_numpy=True)
			res = coll.query(query_embeddings=emb.tolist(), n_results=3, include=["documents"])
			chunks = res.get("documents", [[]])[0]
			rag_chunks.extend(chunks)
		
		print(f"[Meta-Prompt] Found {len(rag_chunks)} RAG chunks")
	except Exception as e:
		# Arrive quand ChromaDB est down ou collection n'existe pas encore
		print(f"[WARNING] RAG fetch failed: {e} - continuing with defaults")
		rag_chunks = []
	
	# Build the prompt (with retry logic in case validation fails)
	for attempt in range(max_retries):
		prompt = _build_prompt(ctx, rag_chunks)
		
		# Basic sanity check
		if len(prompt) > 100 and "RÔLE" in prompt:
			print(f"[Meta-Prompt] ✓ Generated (attempt {attempt+1})")
			return prompt
		
		print(f"[Meta-Prompt] Retry {attempt+1}: prompt too short or malformed")
	
	# Fallback: return whatever we got
	print("[Meta-Prompt] ⚠ Validation failed but returning anyway")
	return prompt
