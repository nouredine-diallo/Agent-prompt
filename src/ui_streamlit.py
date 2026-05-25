import streamlit as st
import json
import os
import sys

def main():
    # Definition du Frontend avec streamlit pour interagir avec l'Agent
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.exists("chroma_db"):
        st.write("Initialisation de la base vectorielle (Ingestion)...")
        from src.ingestion import run_ingestion
        run_ingestion() 

    from src.agent_core import (
        generate_prompt_with_metadata,
        _parse_goal,
    )

    os.environ["NO_PROXY"] = "localhost,127.0.0.1"
    os.environ["no_proxy"] = "localhost,127.0.0.1"

    st.set_page_config(page_title="Meta-Prompting Architect", page_icon="✨", layout="wide")

    st.title("Agent prompt ")
    st.caption("Generate optimized, structured, and secure prompts from your goals.")

    st.info("Describe what you want to accomplish → get an optimized prompt")

    goal = st.text_area(
        "📝 Your goal:",
        placeholder="Example: 'Extract email addresses from PDFs'\n"
                    "Example: 'Classify tweets as positive/negative with data protection'\n"
                    "Example: 'Summarize medical reports in JSON format'",
        height=100
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        gen_btn = st.button(" Generate Prompt", type="primary")
    with col2:
        if goal:
            st.caption(f"{len(goal.split())} words")

    if gen_btn:
        if not goal or len(goal.strip()) < 10:
            st.warning(" Please provide more details (at least 10 chars)")
        else:
            with st.spinner(" Generating prompt (Parse → RAG → Build → Validate)..."):
                try:
                    # Appel direct a l'agent
                    prompt_result = generate_prompt_with_metadata(goal)
                    prompt_out = prompt_result["prompt"]

                    if prompt_result["mode"] == "fallback_template":
                        st.warning(
                            f"🛡️ Fallback template used: {prompt_result['fallback_reason']}"
                        )
                    else:
                        st.success("✅ Prompt generated successfully with Groq (Llama 3.1)")

                    st.markdown("####  Your optimized prompt:")
                    st.code(prompt_out, language="markdown")

                    st.download_button(
                        label="⬇ Download Prompt",
                        data=prompt_out,
                        file_name="optimized_prompt.txt",
                        mime="text/plain"
                    )

                    with st.expander(" Analyse interne (Debug)"):
                        ctx = _parse_goal(goal)
                        st.markdown("**1. Objectif parsé :**")
                        st.json(ctx)
                        st.markdown("**2. Traçabilité (Data Lineage) :**")
                        st.json(
                            {
                                "mode": prompt_result["mode"],
                                "fallback_reason": prompt_result["fallback_reason"],
                                "sources": prompt_result["sources"],
                                "reasoning_steps": prompt_result["reasoning_steps"],
                            }
                        )

                except Exception as e:
                    st.error(f"❌ Generation failed: {e}")
                    st.exception(e)

    # Section aide
    with st.expander(" Tips for better prompts"):
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

if __name__ == "__main__":
    main()