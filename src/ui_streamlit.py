import streamlit as st
import requests
import json
import uuid
import os
import sys

# Hack import - conflit fichier agent.py vs dossier agent/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("agent_mod", os.path.join(os.path.dirname(__file__), "agent.py"))
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)
generer_meta_prompt = agent_mod.generer_meta_prompt

st.set_page_config(page_title="Meta-Prompting Architect 🤖", page_icon="🤖", layout="wide")

# Config API
API_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
API_PORT = int(os.getenv("FASTAPI_PORT", 8000))
API_URL = f"http://{API_HOST}:{API_PORT}/generate"
API_STATUS = f"http://{API_HOST}:{API_PORT}/"

st.title("🤖 Meta-Prompting Architect")
st.caption("Q&A RAG or Prompt Generation")

# Sélecteur de mode
mode = st.radio(
    "Choose mode:",
    ["💬 Q&A RAG", "✨ Generate Prompt"],
    help="Q&A: ask questions. Generate: get optimized prompts from goals."
)

# ============================================================================
# MODE 1: Q&A RAG
# ============================================================================
if mode == "💬 Q&A RAG":
    st.markdown("### 💬 Ask about Prompt Engineering")
    
    # Vérifier si l'API est accessible
    api_ok = False
    try:
        r = requests.get(API_STATUS, timeout=5)
        if r.ok and r.json().get("status") == "Agent-Prompt API is running":
            api_ok = True
    except:
        pass

    if not api_ok:
        st.error(f"⚠️ API not reachable at {API_STATUS}\n\n"
                 f"Start it with: `uvicorn src.api:app --host {API_HOST} --port {API_PORT} --reload`")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Afficher l'historique du chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            elif isinstance(msg["content"], dict) and "answer" in msg["content"]:
                st.markdown(msg["content"]["answer"])
                with st.expander("📜 Details (sources, meta)"):
                    st.json(msg["content"])
            else:
                st.error(str(msg["content"]))

    query = st.chat_input("What prompt do you need help with?")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("🧠 Agent thinking (RAG + CoT + validation)...")
            
            try:
                qid = str(uuid.uuid4())
                payload = {"query_text": query, "query_id": qid}
                resp = requests.post(API_URL, json=payload, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                
                placeholder.markdown(data.get("answer", "*No answer received*"))
                with st.expander("📜 Details (sources, meta)"):
                    st.json(data)
                
                st.session_state.messages.append({"role": "assistant", "content": data})
            
            except requests.exceptions.ConnectionError:
                err = f"Can't connect to API at {API_URL}. Did you start the server?"
                placeholder.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except requests.exceptions.Timeout:
                err = "Timeout: API didn't respond in 120s"
                placeholder.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except Exception as e:
                err = f"Unexpected error: {e}"
                placeholder.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

# ============================================================================
# MODE 2: GÉNÉRATION DE PROMPT
# ============================================================================
else:
    st.markdown("### ✨ Prompt Generation")
    st.info("Describe what you want to accomplish → get an optimized prompt")
    
    goal = st.text_area(
        "🎯 Your goal:",
        placeholder="Example: 'Extract email addresses from PDFs'\n"
                    "Example: 'Classify tweets as positive/negative with data protection'\n"
                    "Example: 'Summarize medical reports in JSON format'",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        gen_btn = st.button("✨ Generate", type="primary")
    with col2:
        if goal:
            st.caption(f"📊 {len(goal.split())} words")
    
    if gen_btn:
        if not goal or len(goal.strip()) < 10:
            st.warning("⚠️ Please provide more details (at least 10 chars)")
        else:
            with st.spinner("🧠 Generating prompt (parse → RAG → build → validate)..."):
                try:
                    # Appel du générateur
                    prompt_out = generer_meta_prompt(goal)
                    
                    st.success("✅ Prompt generated!")
                    
                    st.markdown("#### 📋 Your optimized prompt:")
                    st.code(prompt_out, language="markdown")
                    
                    # Bouton téléchargement
                    st.download_button(
                        label="💾 Download Prompt",
                        data=prompt_out,
                        file_name="optimized_prompt.txt",
                        mime="text/plain"
                    )
                    
                    # Infos debug
                    with st.expander("🔍 Debug (internal parse)"):
                        ctx = agent_mod._parse_goal(goal)
                        st.json(ctx)
                        st.caption("This context was used to build the prompt above")
                
                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")
                    st.exception(e)
    
    # Section aide
    with st.expander("❓ Tips for better prompts"):
        st.markdown("""
        **How to write good goals:**
        
        1. **Be specific**: State clearly what to extract/classify/summarize
        2. **Mention format**: JSON? Text? List?
        3. **Add context**: PDF, email, article, medical data, etc.
        4. **Security**: If handling sensitive data, say "with security" or "confidential"
        
        **Good examples:**
        - ✅ "Extract email addresses and phone numbers from CVs in JSON format"
        - ✅ "Classify customer reviews as positive/negative/neutral with privacy protection"
        - ✅ "Summarize technical documentation keeping only key features"
        - ❌ "do something with data" (too vague)
        """)
