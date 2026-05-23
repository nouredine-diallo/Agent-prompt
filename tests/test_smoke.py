from pathlib import Path
import json

#TEST UNITAIRE DE VALIDATION DU FORMAT DATASET JSON , QUE CHAQUE SOURCE ATTENDUE EXISTE , VERIFICATION DES CONCEPTS DE BASE ( rag ,chunk , prompt engeneering ...)
REPO_ROOT = Path(__file__).resolve().parents[1]
QUERIES_PATH = REPO_ROOT / "tests" / "queries_agent_20.jsonl"
RAG_PATH = REPO_ROOT / "docs" / "txt" / "RAG.txt"
PROMPT_GUIDE_PATH = REPO_ROOT / "docs" / "txt" / "prompt-engineering.txt"


def load_queries(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def test_queries_file_contains_expected_entries():
    rows = load_queries(QUERIES_PATH)

    assert len(rows) == 20
    assert all("query" in row for row in rows)
    assert all("ground_truth" in row for row in rows)
    assert all("scenario_type" in row for row in rows)
    assert all("expected_sources" in row for row in rows)


def test_expected_sources_exist_on_disk():
    rows = load_queries(QUERIES_PATH)

    for row in rows:
        for source in row["expected_sources"]:
            assert (REPO_ROOT / source).exists(), f"Source missing: {source}"


def test_rag_document_mentions_chunking_concepts():
    text = RAG_PATH.read_text(encoding="utf-8")

    assert "chunk_size" in text
    assert "chunk_overlap" in text
    assert "Retrieval-Augmented Generation" in text


def test_prompt_guide_mentions_json_and_ambiguity():
    text = PROMPT_GUIDE_PATH.read_text(encoding="utf-8")

    assert "Debug invalid JSON" in text
    assert "Avoid ambiguity" in text
