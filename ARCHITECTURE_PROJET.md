# Architecture Système : Agent-Prompt

## 1. Vue d'Ensemble & Objectif Métier
**Agent-Prompt** est un pipeline d'orchestration LLM conçu pour générer des instructions (prompts)  structurées et sécurisées. 

Le système résout le problème des hallucinations et des formats imprévisibles des LLMs en combinant la récupération documentaire (RAG) avec un flux d'exécution hybride : le LLM est contraint par des schémas stricts (Structured Output) et le système bascule sur un générateur déterministe (Fallback) en cas de faille de sécurité ou d'indisponibilité.

---

## 2. Architecture en 4 Couches

```text
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE 4 : INTERFACE                     │
│  src/ui_streamlit.py → Interface utilisateur & Dataviz      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE 3 : API REST                      │
│  src/api.py → Serveur FastAPI (Endpoints & Pydantic)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE 2 : ORCHESTRATION                   │
│  src/agent_core.py → Pipeline Hybride (Groq LLM / Fallback) │
│  src/validator.py  → Guardrails (Sécurité & PII Regex)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE 1 : DATA & RAG                      │
│  src/ingestion.py → Chunking Sémantique & Idempotence       │
│  chroma_db/       → Base Vectorielle (all-MiniLM-L6-v2)     │
└─────────────────────────────────────────────────────────────┘