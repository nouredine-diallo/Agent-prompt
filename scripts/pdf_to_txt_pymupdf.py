#!/usr/bin/env python3
# scripts/pdf_to_txt_pymupdf.py
# Extrait texte de PDFs via PyMuPDF (fitz) et écrit dans docs/txt/
# Usage: python scripts/pdf_to_txt_pymupdf.py

import os
import glob
import fitz  # pip install pymupdf

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(BASE, "docs")
TXT_DIR = os.path.join(DOCS, "txt")
PDF_GLOBS = [
    os.path.join(DOCS, "downloads", "*.pdf"),
    os.path.join(DOCS, "arxiv", "*.pdf"),
    os.path.join(DOCS, "*.pdf"),
]

os.makedirs(TXT_DIR, exist_ok=True)

def extract_pdf_to_txt(pdf_path, out_path):
    try:
        doc = fitz.open(pdf_path)
        parts = []
        for page in doc:
            text = page.get_text("text")
            if text:
                parts.append(text)
        content = "\n\n--- Page Suivante ---\n\n".join(parts)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    pdf_files = []
    for pattern in PDF_GLOBS:
        pdf_files.extend(glob.glob(pattern))
    pdf_files = sorted(set(pdf_files))
    print(f"Found {len(pdf_files)} PDF files to convert.")
    converted = 0
    errors = []
    for pdf in pdf_files:
        name = os.path.basename(pdf)[:-4]
        out = os.path.join(TXT_DIR, f"{name}.txt")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            print(f"Skip (exists): {out}")
            continue
        ok, err = extract_pdf_to_txt(pdf, out)
        if ok:
            print(f"Converted: {pdf} -> {out}")
            converted += 1
        else:
            print(f"ERROR converting {pdf}: {err}")
            errors.append((pdf, err))
    print(f"Conversion finished. Converted: {converted}, Errors: {len(errors)}")
    if errors:
        print("Errors (sample):")
        for p,e in errors[:10]:
            print(p, "->", e)

if __name__ == "__main__":
    main()
