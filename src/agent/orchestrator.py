"""
Orchestrator - Le "Système Nerveux" de l'Agent
Connecte le Cerveau (SYSTEM_PROMPT) aux Outils (RAG)
"""

import sys
import os

# Ajuster le path pour imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Livre de recettes : le system prompt
from prompts.meta_architect_prompt import SYSTEM_PROMPT, build_meta_prompt

# 
import importlib.util
spec = importlib.util.spec_from_file_location("agent", os.path.join(parent_dir, "agent.py"))
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
generate_with_checks = agent_module.generate_with_checks


def create_meta_agent():
    """
    Assemble et retourne l'agent orchestrateur simplifié.
    Pour l'instant : retourne une fonction qui combine RAG + prompt assembly.
    """
    
    def agent_run(user_objective: str) -> dict:
        """
        Exécute l'orchestration manuelle :
        1. Récupérer contexte RAG
        2. Construire le prompt avec SYSTEM_PROMPT
        3. Retourner résultat structuré
        """
        # Étape 1 : Chercher dans le RAG
        rag_result = generate_with_checks(query_text=user_objective, k=5)
        rag_context = rag_result.get("answer", "")
        sources = rag_result.get("sources", [])
        
        # Étape 2 : Construire le meta-prompt
        full_prompt = build_meta_prompt(user_objective, rag_context)
        
        # Étape 3 : Retourner (pour l'instant, sans appel LLM)
        return {
            "prompt_generated": full_prompt,
            "sources_rag": sources,
            "user_objective": user_objective,
            "rag_context_preview": rag_context[:500] + "..." if len(rag_context) > 500 else rag_context
        }
    
    return agent_run