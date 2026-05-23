"""
Évaluation du pipeline RAG avec Ragas.
Métriques mesurées : faithfulness, answer_relevancy, context_precision
Dataset : queries_agent_20.jsonl  
"""

import json
from datasets import Dataset
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

def load_queries(path: str) -> list[dict]:
    """Charge les 20 requêtes  de queries_agent_20.json du gold set."""
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
        
        ground_truth = q.get("ground_truth", "") 
        
        # Appel de l'agent
        result = agent_fn(question)
        
        #on map les bonne clé 
        answer = result.get("answer", "")
        contexts = result.get("contexts", []) 
        
        rows.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth,
        })
    
    return Dataset.from_list(rows) 

def run_evaluation(dataset) -> dict:
    """
    Lance l'évaluation Ragas 
    """

    

    evaluator_llm = ChatOllama(model="llama3")
    
    #model embedding pour calculer les similarité dans les reponses et context 
    evaluator_embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    print("[INFO] Lancement de l'évaluation Ragas ")
    
   
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )
    
    return result
if __name__ == "__main__":
    import os
  
    from src.agent import generate_with_checks

   
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gold_set_path = os.path.join(base_dir, "tests", "queries_agent_20.jsonl")

    print(f"Chargement du gold set depuis {gold_set_path}...")
    try:
        queries = load_queries(gold_set_path)
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {gold_set_path}. Vérifiez l'emplacement.")
        exit(1)

    print(f"Génération des réponses pour {len(queries)} requêtes...")
    # on construit le dataset Ragas  
    dataset = build_ragas_dataset(queries, generate_with_checks)

    print("Évaluation Ragas en cours ")
    results = run_evaluation(dataset)

    print(" RÉSULTATS GLOBAUX")
    for metric, score in results.items():
        print(f"{metric}: {score:.3f}")

    output_path = os.path.join(base_dir, "evaluation_results.json")
    with open(output_path, "w") as f:
        json.dump(dict(results), f, indent=2)
    print(f"\nRésultats sauvegardés dans {output_path}")