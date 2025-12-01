import re
import sys
import pdfplumber
import os

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "RAG.pdf")
URLS_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "urls_from_pdf.txt")
GITHUB_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "github_from_pdf.txt")

def extract_urls_from_pdf(pdf_path):
    urls = set()
    github_urls = set()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                found = re.findall(r'https?://\S+', text)
                for u in found:
                    u = u.strip(".,);]'\"")
                    urls.add(u)
                    if re.match(r'https?://(www\.)?github\.com/[^\s/]+/[^\s/]+', u):
                        github_urls.add(u)
    except Exception as e:
        print(f"ERREUR extraction PDF: {e}", file=sys.stderr)
    return urls, github_urls

def main():
    urls, github_urls = extract_urls_from_pdf(PDF_PATH)
    with open(URLS_OUT, "w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")
    with open(GITHUB_OUT, "w", encoding="utf-8") as f:
        for u in sorted(github_urls):
            f.write(u + "\n")
    print(f"Extraction terminée. {len(urls)} URLs, {len(github_urls)} URLs GitHub.")

if __name__ == "__main__":
    main()