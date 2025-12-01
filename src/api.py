import os
import uvicorn
import uuid
import sys
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# Hack import - fichier agent.py (pas le dossier agent/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
agent_path = os.path.join(os.path.dirname(__file__), 'agent.py')
spec = importlib.util.spec_from_file_location("agent_core", agent_path)
agent_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_core)
generate_with_checks = agent_core.generate_with_checks

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="Agent-Prompt API",
    description="Meta-Prompting Architect API",
    version="1.0.0"
)

class GenReq(BaseModel):
    query: str
    mock: Optional[bool] = False
    max_tokens: Optional[int] = 512
    query_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

# CORS pour l'UI Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def status():
    return {"status": "Agent-Prompt API is running"}


@app.post("/generate")
async def generate(req: GenReq = Body(...)):
    """Main endpoint - runs full agent pipeline"""
    if not os.getenv("OPENAI_API_KEY") and not req.mock:
        pass  # RAG fonctionne sans clé

    try:
        print(f"[{req.query_id[:8]}] Query: '{req.query[:50]}...'")

        if req.mock:
            return {
                "answer": f"Mock response for: {req.query}",
                "sources": [],
                "metadata": {"query_id": req.query_id, "mock": True, "failure_reason": "ok"}
            }

        # Appel du moteur agent
        result = generate_with_checks(
            query_text=req.query,
            query_id=req.query_id
        )

        # Vérifier que sources existe
        if "sources" not in result:
            result["sources"] = []
        
        print(f"[{req.query_id[:8]}] Done")
        return result

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Agent processing failed")

if __name__ == "__main__":
    print("Starting API on http://127.0.0.1:8000")
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
