# scripts/generate_urls_extra.py
# Génère urls_extra.txt avec les sources officielles, arXiv queries, et repos fallback
urls = [
    # OpenAI docs
    "https://platform.openai.com/docs/guides/rag",
    "https://platform.openai.com/docs/guides/prompt-engineering/best-practices",
    "https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering",
    "https://platform.openai.com/docs/guides/gpt/system-messages",
    # LangChain docs
    "https://python.langchain.com/docs/get_started/introduction",
    "https://github.com/hwchase17/langchain",
    # Hugging Face
    "https://huggingface.co/blog/sentence-transformers",
    "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
    # ArXiv queries (to be handled by fetch_data.py)
    "arxiv:retrieval augmented generation",
    "arxiv:chain of thought",
    "arxiv:instruction tuning",
    # Fallback repos
    "https://github.com/jerryjliu/llama_index",
    "https://github.com/chromadb/chroma",
    "https://github.com/UKPLab/sentence-transformers",
    "https://github.com/huggingface/transformers"
]
with open("urls_extra.txt", "w", encoding="utf-8") as f:
    for url in urls:
        f.write(url+"\n")
print(f"urls_extra.txt généré avec {len(urls)} URLs.")
