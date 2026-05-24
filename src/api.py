import os
import uvicorn
import sys
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware

# Importation sécurisée
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent_core import generate_prompt_with_metadata

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="Agent-Prompt API",
    description="API for the Meta-Prompting Architect - Generate structured prompts.",
    version="1.0.0"
)

# Utilisation de Pydantic pour valider la requête utilisateur
class GeneratePromptReq(BaseModel):
    goal: str
    mock: Optional[bool] = False

# Utilisation de Pydantic pour documenter et valider la réponse
class GeneratePromptRes(BaseModel):
    prompt: str
    mode: str
    fallback_reason: Optional[str]
    sources: List[str]
    reasoning_steps: List[str]

# CORS pour autoriser l'accès depuis n'importe quel frontend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def status():
    return {"status": "Agent-Prompt API is running"}


@app.post("/generate", response_model=GeneratePromptRes)
async def generate(req: GeneratePromptReq = Body(...)):
    """Génère un prompt optimisé basé sur un objectif métier """
    try:
        print(f"Goal received: '{req.goal[:50]}...'")

        if req.mock:
            return {
                "prompt": f"Mock prompt generated for: {req.goal}",
                "mode": "mock",
                "fallback_reason": None,
                "sources": ["mock_source.txt"],
                "reasoning_steps": ["1. Mock analysis completed."]
            }

        
        result = generate_prompt_with_metadata(goal=req.goal)
        
        print("Prompt generation done.")
        return result

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Prompt generation failed")

if __name__ == "__main__":
    print("Starting API on http://127.0.0.1:8000")
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)