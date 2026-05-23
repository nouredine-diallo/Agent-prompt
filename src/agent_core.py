
import os
import json

import chromadb
import ollama
from sentence_transformers import SentenceTransformer

from prompts.meta_architect_prompt import  (
    FEW_SHOT_EXAMPLES,
    JSON_OUTPUT_SCHEMA,
    SECURITY_GUARDRAILS,
    SYSTEM_PROMPT,
    build_meta_prompt,
    validate_generated_prompt,
)

MODEL = "all-MiniLM-L6-v2"
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")


def _normalize_source(meta):
    src = (meta or {}).get("source") or (meta or {}).get("title")
    if not src:
        return ""
    rel = os.path.relpath(src, os.path.dirname(os.path.dirname(__file__)))
    return rel.replace("\\", "/")


def _retrieve_documents(query_text, k=5):
    model = SentenceTransformer(MODEL)
    client = chromadb.PersistentClient(path=DB_DIR)
    col = client.get_or_create_collection("docs")

    q_emb = model.encode([query_text], convert_to_numpy=True)
    res = col.query(
        query_embeddings=q_emb.tolist(),
        n_results=k,
        include=["documents", "metadatas"],
    )

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return docs, metas


def _build_llm_system_prompt():
    return "\n\n".join( 
        [
            SYSTEM_PROMPT,
            "=== SECURITY_GUARDRAILS ===",
            SECURITY_GUARDRAILS,
            "=== JSON_OUTPUT_SCHEMA ===",
            json.dumps(JSON_OUTPUT_SCHEMA, ensure_ascii=False, indent=2),
            "=== FEW_SHOT_EXAMPLES ===",
            json.dumps(FEW_SHOT_EXAMPLES[:1], ensure_ascii=False, indent=2), 
        ]
    )


def _build_llm_user_prompt(goal, ctx, rag_chunks):
    rag_context = "\n\n".join(rag_chunks[:6]) if rag_chunks else "[Aucun chunk RAG disponible]"
    contract = {
        "goal": goal,
        "task": ctx["task"],
        "format": ctx["format"],
        "security": ctx["security"],
        "target": ctx["target"],
    }

    return (
        f"{build_meta_prompt(goal, rag_context)}\n\n"
        f"=== JSON_CONTRACT ===\n{json.dumps(contract, ensure_ascii=False, indent=2)}"
    )


def _validate_llm_payload(payload):
    if not isinstance(payload, dict):
        return {"valid": False, "errors": ["LLM output is not a JSON object"], "warnings": []}

    validation = validate_generated_prompt(json.dumps(payload, ensure_ascii=False))
    if validation.get("valid"):
        return validation

    if not isinstance(payload.get("prompt_final"), str) or not payload.get("prompt_final", "").strip():
        validation["errors"].append("prompt_final must be a non-empty string")

    if not isinstance(payload.get("sources_rag"), list):
        validation["errors"].append("sources_rag must be a list")

    return validation


def _build_fallback_result(prompt, sources, reason):
    return {
        "prompt": prompt,
        "mode": "fallback_template",
        "fallback_reason": reason,
        "sources": sources,
        "reasoning_steps": [
            "Fallback template used because the LLM output was invalid or unavailable."
        ],
    }


def _invoke_ollama(model_name, messages, llm_client=None):
    if llm_client is not None:
        return llm_client.chat(model=model_name, messages=messages, format="json")

    return ollama.chat(model=model_name, messages=messages, format="json",host="http://127.0.0.1:11434")




def generate_with_checks(query_text, query_id=None, k=5): #similaire a retreve test de l'ingestion sauf qu'on normalise les chemins
    """RAG pipeline: embed query, search ChromaDB, return chunks"""
    try:
        answers, metas = _retrieve_documents(query_text, k=k)
        sources = [_normalize_source(m) for m in metas if _normalize_source(m)]
        answer = "\n---\n".join(answers[:k]) if answers else "No results found"

        print(f"[{query_id[:8] if query_id else 'N/A'}] sources: {len(sources)}")

        return {
            "answer": answer,
            "contexts": answers[:k],
            "sources": sources,
            "metadata": {"query_id": query_id, "failure_reason": "ok"},
        }
    except Exception as e:
        return {
            "answer": "",
            "contexts": [],
            "sources": [],
            "metadata": {"query_id": query_id, "failure_reason": str(e)},
        }


# Générer des prompts optimisés depuis des objectifs

def _parse_goal(goal: str):
	""" détecte task type, format, security flags"""
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
	
	# Extraire données cible 
	target = goal
	for keyword in ["extraire", "classifier", "résumer", "valider"]:
		if keyword in txt:
			parts = txt.split(keyword, 1)
			if len(parts) > 1:
				# Grab first few words after the verb
				target = " ".join(parts[1].strip().split()[:5])
				break
	
	print(f"Parsed goal: task={task}, fmt={fmt}, security={needs_security}")
	
	return {
		"task": task,
		"format": fmt,
		"security": needs_security,
		"target": target
	}


def _build_prompt(ctx: dict, rag_chunks: list = None) -> str:
	"""Assemble le prompt final - template-based approach"""
	
	# Mapping rôle 
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
		json_schema = """Retourne un JSON avec cette structure :
{
  "resultat": [...],
  "confiance": 0.0-1.0,
  "source": "..."
}"""
		# Essayer d'extraire un schéma depuis RAG si disponible
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
	
	# Exemples (
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
	
	# recup le premier chunk de contrainte du rag 
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


def _fetch_prompt_context(ctx):
    rag_chunks = []
    sources = []

    queries = [
        f"techniques de prompt pour {ctx['task']}",
        f"structurer un prompt pour {ctx['format']}",
    ]
    if ctx.get("security"):
        queries.append("guardrails de sécurité dans les prompts")

    for query in queries:
        docs, metas = _retrieve_documents(query, k=3)
        rag_chunks.extend(docs)
        sources.extend([_normalize_source(meta) for meta in metas if _normalize_source(meta)])

    return rag_chunks, list(dict.fromkeys(sources))


def generate_prompt_with_metadata(goal, rag_chunks=None, llm_client=None, model=None):
    """construit un prompt base sur RAG + LLM generation et template based si fallback """
    ctx = _parse_goal(goal)
    if rag_chunks is None:
        rag_chunks, sources = _fetch_prompt_context(ctx)
    else:
        sources = []

    fallback_prompt = _build_prompt(ctx, rag_chunks)
    fallback_result = _build_fallback_result(
        fallback_prompt,
        sources,
        "LLM output unavailable; using the template-based fallback.",
    )

    if llm_client is None:
        llm_client = ollama

    try:
        messages = [
            {"role": "system", "content": _build_llm_system_prompt()},
            {"role": "user", "content": _build_llm_user_prompt(goal, ctx, rag_chunks)},
        ]

        raw_response = _invoke_ollama(model or OLLAMA_MODEL, messages, llm_client=llm_client)
        payload = raw_response.get("message", {}).get("content") if isinstance(raw_response, dict) else raw_response

        if isinstance(payload, str):
            payload = json.loads(payload)

        validation = _validate_llm_payload(payload)
        if not validation.get("valid", False):
            fallback_result["fallback_reason"] = "; ".join(validation.get("errors", ["LLM validation failed"]))
            return fallback_result

        menu_sources = payload.get("sources_rag") or sources
        reasoning_steps = payload.get("reasoning_steps") or [
            "LLM generated the prompt using the hybrid RAG + constraints workflow."
        ]

        return {
            "prompt": payload["prompt_final"].strip(),
            "mode": "llm",
            "fallback_reason": None,
            "sources": menu_sources,
            "reasoning_steps": reasoning_steps,
        }
    except Exception as exc:
        fallback_result["fallback_reason"] = f"fallback_template: {exc}"
        return fallback_result


def generer_meta_prompt(goal: str, max_retries: int = 2) -> str:
    """Appelle le pipeline complet , recup le prompt final de l'etape precedente """
    result = generate_prompt_with_metadata(goal)
    return result["prompt"]


  