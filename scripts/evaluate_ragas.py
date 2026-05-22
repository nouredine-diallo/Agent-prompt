"""
Évaluation du pipeline RAG avec Ragas.
Métriques mesurées : faithfulness, answer_relevancy, context_precision
Dataset : queries_agent_20.jsonl (20 requêtes annotées manuellement)
"""

import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

def load_queries(path: str) -> list[dict]:
    """Charge les 20 requêtes du gold set."""
    queries = []
    with open(path) as f:
        for line in f:
            queries.append(json.loads(line))
    return queries

def build_ragas_dataset(queries: list[dict], agent_fn) -> Dataset:
    """
    Génère les réponses de l'agent pour chaque requête et construit le dataset Ragas.
    """
    rows = []
    for q in queries:
        question = q["query"]
        ground_truth = q.get("expected_answer", "")
        
        # Appeler l'agent et récupérer réponse + contextes (À adapter selon ton architecture)
        result = agent_fn(question)
        answer = result["answer"]
        contexts = result["retrieved_contexts"]  # liste de strings
        
        rows.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth,
        })
    
    return Dataset.from_list(rows)

def run_evaluation(dataset: Dataset) -> dict:
    """Lance l'évaluation Ragas et retourne les métriques."""
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    return result

if __name__ == "__main__":
    from src.agent import run_agent # Import à adapter
    
    print("Chargement du gold set...")
    queries = load_queries("data/queries_agent_20.jsonl")
    
    print(f"Génération des réponses pour {len(queries)} requêtes...")
    dataset = build_ragas_dataset(queries, run_agent)
    
    print("Évaluation Ragas en cours...")
    results = run_evaluation(dataset)
    
    with open("evaluation_results.json", "w") as f:
        json.dump(dict(results), f, indent=2)
    print("\nRésultats sauvegardés dans evaluation_results.json")
