import os
import re
import sys
import glob
import arxiv
import requests
import subprocess
import pdfplumber
from typing import List, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DOWNLOAD_DIR = os.path.join(DOCS_DIR, "downloads")
ARXIV_DIR = os.path.join(DOCS_DIR, "arxiv")
GITHUB_DIR = os.path.join(DOCS_DIR, "github")
TXT_DIR = os.path.join(DOCS_DIR, "txt")
PDF_SOURCE_FILE = os.path.join(DOCS_DIR, "RAG.pdf")
URL_LIST_FILE = os.path.join(BASE_DIR, "urls_fixed.txt") if os.path.exists(os.path.join(BASE_DIR, "urls_fixed.txt")) else os.path.join(BASE_DIR, "urls_from_pdf.txt")
REPO_LIST_FILE = os.path.join(BASE_DIR, "repos.txt")

# --- 1. Download from URL List ---
def download_from_urls():
    print(f"Telechargement depuis cette url  {URL_LIST_FILE}...")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if not os.path.exists(URL_LIST_FILE):
        print("INFO: Fichier d'URLs non trouvé, étape sautée.", file=sys.stderr)
        return
    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()] #enleve les espace dans le fichier pour lire les url 
    for url in urls:
        try: 
            r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})  #  headers pour faire croire qu'on est un humain sur un navigateur
            r.raise_for_status()
            ct = r.headers.get("content-type", "")  #recup le type du fichier ( pdf html....)
            p = urlparse(url).path
            name = os.path.basename(p) or "index"
            if "pdf" in ct or url.lower().endswith(".pdf"):
                path = os.path.join(DOWNLOAD_DIR, name if name.endswith(".pdf") else name + ".pdf")
                with open(path, "wb") as w: w.write(r.content) #mettre le fichier pdf en bin pour le telecharger
                print(f"  Saved PDF: {path}")
            else:
                path = os.path.join(DOWNLOAD_DIR, name if name.endswith(".html") else name + ".html")
                with open(path, "w", encoding="utf-8") as w: w.write(r.text)
                print(f"  Saved HTML: {path}")
        except Exception as e:
            print(f"  ERREUR (Download): {url} - {e}", file=sys.stderr)

# ---  Fetch ArXiv ---
def fetch_arxiv(query: str = "prompt engineering techniques", max_results: int = 10):
    print(f"\n Récupération d'ArXiv (Query: '{query}')...")
    os.makedirs(ARXIV_DIR, exist_ok=True)
    try:
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
        for r in search.results():
            title_safe = "".join(c for c in r.title if c.isalnum() or c in " -_")[:80]
            outpath = os.path.join(ARXIV_DIR, f"{title_safe}.pdf")
            if not os.path.exists(outpath):
                print(f"  Downloading: {r.title}")
                r.download_pdf(filename=outpath)
            else:
                print(f"  Skipping (exists): {r.title}")
    except Exception as e:
        print(f"ERREUR (ArXiv) : {e}", file=sys.stderr)

# --- Clone Repos ---
def clone_repos():
    print(f"\n Clonage des dépôts depuis {REPO_LIST_FILE}...")
    os.makedirs(GITHUB_DIR, exist_ok=True)
    if not os.path.exists(REPO_LIST_FILE):
        print("INFO: Fichier de dépôts non trouvé, étape sautée.", file=sys.stderr)
        return
    with open(REPO_LIST_FILE, "r", encoding="utf-8") as f:
        repos = [r.strip() for r in f if r.strip()]
    for repo in repos:
        try:
            name = os.path.basename(repo)
            if name.endswith(".git"):
                name = name[:-4]
            target_dir = os.path.join(GITHUB_DIR, name)
            if os.path.exists(target_dir):
                print(f"  Skipping (exists): {name}")
            else:
                print(f"  Cloning: {repo}")
                subprocess.run(["git", "clone", repo, target_dir], check=True, capture_output=True)
        except Exception as e:
            print(f"  ERREUR (Git Clone): {repo} - {e}", file=sys.stderr)

# --- 4. Convert PDFs to TXT ---
def convert_pdfs_to_txt():
    print("\n Conversion des PDFs en TXT...")
    os.makedirs(TXT_DIR, exist_ok=True)
    pdf_files = glob.glob(os.path.join(DOCS_DIR, "**/*.pdf"), recursive=True)
    print(f"  {len(pdf_files)} PDFs trouvés à convertir.")
    for pdf in pdf_files:
        txt_filename = os.path.basename(pdf)[:-4] + ".txt"
        txt_path = os.path.join(TXT_DIR, txt_filename)
        if os.path.exists(txt_path):
            continue
        try:
            with pdfplumber.open(pdf) as pdf_f:
                pages = [p.extract_text() or "" for p in pdf_f.pages]
            text = "\n\n--- Page Suivante ---\n\n".join(pages)
            with open(txt_path, "w", encoding="utf-8") as w:
                w.write(text)
            print(f"  Converted: {pdf} -> {txt_path}")
        except Exception as e:
            print(f"  ERREUR (PDF Convert): {pdf} - {e}", file=sys.stderr)

# --- 5. Convert HTML and Code to TXT ---
def convert_others_to_txt():
    print("\n Conversion des HTML/Code en TXT...")
    html_files = glob.glob(os.path.join(DOWNLOAD_DIR, "**/*.html"), recursive=True)
    for html in html_files:
        txt_filename = os.path.basename(html)[:-5] + ".txt"
        txt_path = os.path.join(TXT_DIR, txt_filename)
        if os.path.exists(txt_path): continue
        try:
            with open(html, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                text = soup.get_text(separator="\n", strip=True)
            with open(txt_path, "w", encoding="utf-8") as w: w.write(text)
            print(f"  Converted HTML: {html} -> {txt_path}")
        except Exception as e:
            print(f"  ERREUR (HTML Convert): {html} - {e}", file=sys.stderr)
    code_files = glob.glob(os.path.join(GITHUB_DIR, "**/*.py"), recursive=True) + \
                 glob.glob(os.path.join(GITHUB_DIR, "**/*.md"), recursive=True)
    for code_file in code_files:
        if "site-packages" in code_file or ".venv" in code_file:
             continue
        try:
            relative_path = os.path.relpath(code_file, GITHUB_DIR)
            txt_filename = relative_path.replace(os.sep, "_") + ".txt"
            txt_path = os.path.join(TXT_DIR, txt_filename)
            if os.path.exists(txt_path): continue
            with open(code_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            with open(txt_path, "w", encoding="utf-8") as w: w.write(text)
            print(f"  Converted Code: {code_file} -> {txt_path}")
        except Exception as e:
            print(f"  ERREUR (Code Convert): {code_file} - {e}", file=sys.stderr)

def main():
    print("--- DÉBUT DU SOURCING DE DONNÉES  ---")
    download_from_urls()
    fetch_arxiv(query="prompt engineering techniques", max_results=10)
    clone_repos()
    convert_pdfs_to_txt()
    convert_others_to_txt()
    print("--- FIN DU SOURCING DE DONNÉES ---")

if __name__ == "__main__":
    main()
