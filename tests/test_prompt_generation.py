import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import agent as agent_module


RAG_CHUNKS = [
    "Use few-shot examples to show the expected JSON structure.",
    "Prefer explicit schema and clear validation steps.",
]


def test_generate_prompt_with_metadata_uses_llm_response():
    payload = {
        "prompt_final": "You are a strict JSON extractor.",
        "sources_rag": ["docs/txt/prompt-engineering.txt"],
        "reasoning_steps": ["Analyze goal", "Use RAG", "Generate output"],
    }

    fake_llm = types.SimpleNamespace(
        chat=lambda **kwargs: {
            "message": {"content": json.dumps(payload, ensure_ascii=False)}
        }
    )

    result = agent_module.generate_prompt_with_metadata(
        "Extract email addresses in JSON format",
        rag_chunks=RAG_CHUNKS,
        llm_client=fake_llm,
    )

    assert result["mode"] == "llm"
    assert result["prompt"] == payload["prompt_final"]
    assert result["sources"] == payload["sources_rag"]
    assert result["reasoning_steps"] == payload["reasoning_steps"]


def test_generate_prompt_with_metadata_falls_back_when_llm_output_is_invalid():
    fake_llm = types.SimpleNamespace(
        chat=lambda **kwargs: {
            "message": {"content": "this is not valid JSON"}
        }
    )

    result = agent_module.generate_prompt_with_metadata(
        "Extract email addresses in JSON format",
        rag_chunks=RAG_CHUNKS,
        llm_client=fake_llm,
    )

    assert result["mode"] == "fallback_template"
    assert "fallback" in result["fallback_reason"].lower()
    assert "=== RÔLE ===" in result["prompt"]
    assert result["sources"] == []
