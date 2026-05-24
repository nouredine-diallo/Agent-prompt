import os
import json

import chromadb
import requests

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from src.prompts.meta_architect_prompt import (
    FEW_SHOT_EXAMPLES,
    JSON_OUTPUT_SCHEMA,
    SECURITY_GUARDRAILS,
    SYSTEM_PROMPT,
    build_meta_prompt,
    validate_generated_prompt,
)



load_dotenv()

MODEL = "all-MiniLM-L6-v2"

DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chroma_db",
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")



embedding_model = SentenceTransformer(MODEL)

chroma_client = chromadb.PersistentClient(path=DB_DIR)

collection = chroma_client.get_or_create_collection("docs")


#nettoyer les fichier du RAG , Rendre les chemins de tes fichiers propres, lisibles et compatibles
def _normalize_source(meta):
    src = (meta or {}).get("source") or (meta or {}).get("title")

    if not src:
        return ""

    rel = os.path.relpath(
        src,
        os.path.dirname(os.path.dirname(__file__)),
    )

    return rel.replace("\\", "/")  #remplace les anti-slash par des slash 


def _retrieve_documents(query_text, k=5):
    """
    transformer une phrase en vecteurs, analyser chromadb, et ramener les k meilleurs extraits de texte.
    """

    q_emb = embedding_model.encode(
        [query_text],
        convert_to_numpy=True,
    )

    res = collection.query(
        query_embeddings=q_emb.tolist(),
        n_results=k,
        include=["documents", "metadatas"],
    )

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    return docs, metas




def _call_llm(messages, model_name=None):
    """
    Hosted LLM call using Groq OpenAI-compatible API.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "Missing GROQ_API_KEY environment variable."
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name or LLM_MODEL,
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]

#Logique principale 

def _build_llm_system_prompt():
    return "\n\n".join(
        [
            SYSTEM_PROMPT,
            "=== SECURITY_GUARDRAILS ===",
            SECURITY_GUARDRAILS,
            "=== JSON_OUTPUT_SCHEMA ===",
            json.dumps(
                JSON_OUTPUT_SCHEMA,
                ensure_ascii=False,
                indent=2,
            ),
            "=== FEW_SHOT_EXAMPLES ===",
            json.dumps(
                FEW_SHOT_EXAMPLES[:1],
                ensure_ascii=False,
                indent=2,
            ),
        ]
    )


def _build_llm_user_prompt(goal, ctx, rag_chunks):
    rag_context = (
        "\n\n".join(rag_chunks[:6])
        if rag_chunks
        else "[Aucun chunk RAG disponible]"
    )

    contract = {
        "goal": goal,
        "task": ctx["task"],
        "format": ctx["format"],
        "security": ctx["security"],
        "target": ctx["target"],
    }

    return (
        f"{build_meta_prompt(goal, rag_context)}\n\n"
        f"=== JSON_CONTRACT ===\n"
        f"{json.dumps(contract, ensure_ascii=False, indent=2)}"
    )

#validation du output en temps que json

def _validate_llm_payload(payload):
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ["LLM output is not a JSON object"],
            "warnings": [],
        }

    validation = validate_generated_prompt(
        json.dumps(payload, ensure_ascii=False)
    )

    if validation.get("valid"):
        return validation

    if (
        not isinstance(payload.get("prompt_final"), str)
        or not payload.get("prompt_final", "").strip()
    ):
        validation["errors"].append(
            "prompt_final must be a non-empty string"
        )

    if not isinstance(payload.get("sources_rag"), list):
        validation["errors"].append(
            "sources_rag must be a list"
        )

    return validation


def _build_fallback_result(prompt, sources, reason):
    return {
        "prompt": prompt,
        "mode": "fallback_template",
        "fallback_reason": reason,
        "sources": sources,
        "reasoning_steps": [
            (
                "Fallback template used because "
                "the LLM output was invalid or unavailable."
            )
        ],
    }


#RAG RETRIVIAL

def generate_with_checks(query_text, query_id=None, k=5):
    """
    RAG pipeline:
    - embed query
    - retrieve chunks
    - normalize sources
    """

    try:
        answers, metas = _retrieve_documents(
            query_text,
            k=k,
        )

        sources = [
            _normalize_source(m)
            for m in metas
            if _normalize_source(m)
        ]

        answer = (
            "\n---\n".join(answers[:k])
            if answers
            else "No results found"
        )

        print(
            f"[{query_id[:8] if query_id else 'N/A'}] "
            f"sources: {len(sources)}"
        )

        return {
            "answer": answer,
            "contexts": answers[:k],
            "sources": sources,
            "metadata": {
                "query_id": query_id,
                "failure_reason": "ok",
            },
        }

    except Exception as e:
        return {
            "answer": "",
            "contexts": [],
            "sources": [],
            "metadata": {
                "query_id": query_id,
                "failure_reason": str(e),
            },
        }




def _parse_goal(goal: str):
    """
    Detect task type, output format, security needs.
    """

    txt = goal.lower()

    task = "general"

    if any(
        w in txt
        for w in [
            "extraire",
            "extraction",
            "extract",
            "récupérer",
        ]
    ):
        task = "extraction"

    elif any(
        w in txt
        for w in [
            "classifier",
            "classification",
            "catégoris",
        ]
    ):
        task = "classification"

    elif any(
        w in txt
        for w in [
            "résumer",
            "résumé",
            "summary",
            "synthèse",
        ]
    ):
        task = "résumé"

    elif any(
        w in txt
        for w in [
            "valider",
            "validation",
            "vérifier",
        ]
    ):
        task = "validation"

    fmt = (
        "json"
        if task in ["extraction", "classification"]
        else "texte"
    )

    if (
        " json" in txt
        or "en json" in txt
        or "format json" in txt
    ):
        fmt = "json"

    elif any(
        w in txt
        for w in ["en liste", "liste", "bullet"]
    ):
        fmt = "liste"

    elif any(
        w in txt
        for w in [
            "en texte",
            "texte brut",
            "paragraphe",
            "format texte",
        ]
    ):
        fmt = "texte"

    needs_security = any(
        w in txt
        for w in [
            "sécurité",
            "securite",
            "security",
            "confidentiel",
            "privé",
            "protection",
            "guardrail",
            "safe",
            "rgpd",
        ]
    )

    target = goal

    for keyword in [
        "extraire",
        "classifier",
        "résumer",
        "valider",
    ]:
        if keyword in txt:
            parts = txt.split(keyword, 1)

            if len(parts) > 1:
                target = " ".join(
                    parts[1].strip().split()[:5]
                )
                break

    print(
        f"Parsed goal: "
        f"task={task}, "
        f"fmt={fmt}, "
        f"security={needs_security}"
    )

    return {
        "task": task,
        "format": fmt,
        "security": needs_security,
        "target": target,
    }


#TEMPLATE POUR LE FALLBACK 

def _build_prompt(ctx: dict, rag_chunks=None) -> str:
    """
    Template-based fallback prompt generation.
    """

    roles = {
        "extraction": (
            "Tu es un assistant expert en extraction "
            "de données structurées."
        ),
        "classification": (
            "Tu es un expert en classification "
            "et catégorisation de texte."
        ),
        "résumé": (
            "Tu es un assistant spécialisé "
            "en résumé et synthèse de documents."
        ),
        "validation": (
            "Tu es un expert en validation "
            "et vérification de données."
        ),
    }

    role = roles.get(
        ctx["task"],
        "Tu es un assistant IA professionnel et précis.",
    )

    if ctx["task"] == "extraction":
        task_desc = (
            f"Extrais {ctx['target']} du texte fourni."
        )

    elif ctx["task"] == "classification":
        task_desc = (
            f"Classifie le texte selon {ctx['target']}."
        )

    elif ctx["task"] == "résumé":
        task_desc = (
            f"Résume le texte en te concentrant "
            f"sur {ctx['target']}."
        )

    else:
        task_desc = (
            f"Réalise la tâche suivante : "
            f"{ctx['target']}"
        )

    if ctx["format"] == "json":
        format_spec = """
Retourne un JSON avec cette structure :

{
  "resultat": [...],
  "confiance": 0.0-1.0,
  "source": "..."
}
"""

    elif ctx["format"] == "liste":
        format_spec = (
            "Retourne ta réponse sous forme "
            "de liste à puces."
        )

    else:
        format_spec = (
            "Retourne ta réponse "
            "en texte clair et structuré."
        )

    constraints = [
        "- Vérifie la validité du format",
        "- Indique le niveau de confiance",
    ]

    if ctx.get("security"):
        constraints.extend(
            [
                "- Respecter le RGPD",
                "- Ne pas exposer les données sensibles",
                "- Anonymiser si nécessaire",
            ]
        )

    constraints_text = "\n".join(constraints)

    prompt = f"""
=== RÔLE ===
{role}

=== TÂCHE ===
{task_desc}

=== FORMAT ===
{format_spec}

=== CONTRAINTES ===
{constraints_text}

=== INSTRUCTIONS ===
Suis précisément le format demandé.
"""

    return prompt.strip()


#RAG CONTEXT 
#Construire un contexte t pour le LLM en lançant plusieurs recherches très ciblées.Multi-Query Retrieval
def _fetch_prompt_context(ctx):
    rag_chunks = []
    sources = []

    queries = [
        f"techniques de prompt pour {ctx['task']}",
        f"structurer un prompt pour {ctx['format']}",
    ]

    if ctx.get("security"):
        queries.append(
            "guardrails de sécurité dans les prompts"
        )

    for query in queries:
        docs, metas = _retrieve_documents(
            query,
            k=3,
        )

        rag_chunks.extend(docs)

        sources.extend(
            [
                _normalize_source(meta)
                for meta in metas
                if _normalize_source(meta)
            ]
        )

    return rag_chunks, list(dict.fromkeys(sources))


#LOGIQUE PRINCIPALE 

def generate_prompt_with_metadata(
    goal,
    rag_chunks=None,
    model=None,
):
    """
    Hybrid pipeline:
    - parse goal
    - retrieve RAG context
    - generate with hosted LLM
    - validate output
    - fallback if needed
    """

    ctx = _parse_goal(goal)

    if rag_chunks is None:
        rag_chunks, sources = _fetch_prompt_context(ctx)
    else:
        sources = []

    fallback_prompt = _build_prompt(
        ctx,
        rag_chunks,
    )

    fallback_result = _build_fallback_result(
        fallback_prompt,
        sources,
        "LLM unavailable; using fallback template.",
    )

    try:
        messages = [
            {
                "role": "system",
                "content": _build_llm_system_prompt(),
            },
            {
                "role": "user",
                "content": _build_llm_user_prompt(
                    goal,
                    ctx,
                    rag_chunks,
                ),
            },
        ]

        raw_response = _call_llm(
            messages,
            model_name=model or LLM_MODEL,
        )

        payload = json.loads(raw_response)

        validation = _validate_llm_payload(payload)

        if not validation.get("valid", False):
            fallback_result["fallback_reason"] = (
                "; ".join(
                    validation.get(
                        "errors",
                        ["LLM validation failed"],
                    )
                )
            )

            return fallback_result

        menu_sources = (
            payload.get("sources_rag")
            or sources
        )

        reasoning_steps = (
            payload.get("reasoning_steps")
            or [
                (
                    "LLM generated the prompt "
                    "using hybrid RAG workflow."
                )
            ]
        )

        return {
            "prompt": payload["prompt_final"].strip(),
            "mode": "llm",
            "fallback_reason": None,
            "sources": menu_sources,
            "reasoning_steps": reasoning_steps,
        }

    except Exception as exc:
        fallback_result["fallback_reason"] = (
            f"fallback_template: {exc}"
        )

        return fallback_result




def generer_meta_prompt(
    goal: str,
    max_retries: int = 2,
) -> str:
    """
    Recupere le prompt generer de l'etape precedente 
    """

    result = generate_prompt_with_metadata(goal)

    return result["prompt"]