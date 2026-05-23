#!/usr/bin/env python3
# scripts/generate_source_map.py
# Génère source_map.json pour tous les .txt de docs/txt/ à partir des dossiers downloads, arxiv, github
import os
import glob
import json
from datetime import datetime

def find_source(txt_path):
    base = os.path.basename(txt_path)
    # Recherche dans downloads, arxiv, github
    candidates = []
    for sub in ["downloads", "arxiv", "github"]:
        for root, dirs, files in os.walk(os.path.join("docs", sub)):# on va parcourir docs qui est dans downloads arxiv github 
            for f in files:
                if f.lower().replace('.pdf','').replace('.md','').replace('.html','') in base.lower():
                    candidates.append(os.path.join(root, f))# on construit le chemin complet du fichier 
    if candidates:
        return candidates[0] retourne le premier 
    return None

def guess_url_and_author(txt_path, source_path):#le but de cette fonction n'est pas de trouver exactement mais de deviner la source en fonction de la structure de source_path
    url, author = None, None
    if source_path:
        # Si HTML, MD, PDF téléchargé, tente de retrouver l'URL dans le nom ou le dossier
        if source_path.endswith('.html') or source_path.endswith('.md'):
            # Si le nom du dossier est une URL encodée
            parent = os.path.basename(os.path.dirname(source_path))
            if parent.startswith('http'):
                url = parent
        # Si arxiv, tente de retrouver l'id
        if '/arxiv/' in source_path:
            arxiv_id = os.path.splitext(os.path.basename(source_path))[0]
            url = f'https://arxiv.org/abs/{arxiv_id}'
   
    return url, author

def main():
    txt_files = glob.glob('docs/txt/*.txt')
    mapping = {}
    for txt in txt_files:
        source = find_source(txt)
        url, author = guess_url_and_author(txt, source)
        mapping[os.path.basename(txt)] = {   # on construit le dictionnaire mapping qui remplira le json 
            "source_url": url or "",
            "original_file": source or "",
            "date": datetime.fromtimestamp(os.path.getmtime(txt)).isoformat(),
            "author": author or ""
        }
    with open('source_map.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False) parametre de construction d'un json 
    print(f"source_map.json généré avec {len(mapping)} entrées.")

if __name__ == "__main__":
    main()
