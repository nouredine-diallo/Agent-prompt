#!/usr/bin/env python3
"""
Test simple du Meta-Prompting
"""
import sys
import os

# Import direct depuis le fichier agent.py (pas le dossier agent/)
import importlib.util
agent_path = os.path.join(os.path.dirname(__file__), 'src', 'agent.py')
spec = importlib.util.spec_from_file_location("agent_module", agent_path)
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

generer_meta_prompt = agent_module.generer_meta_prompt
_parse_goal = agent_module._parse_goal

def test_extraction_email():
    """Test simple : génération prompt extraction email"""
    print("=" * 80)
    print("TEST 1: Extraction d'emails")
    print("=" * 80)
    
    objectif = "Je veux extraire des emails d'un texte"
    print(f"\nObjectif: {objectif}\n")
    
    # Analyse
    analyse = _parse_goal(objectif)
    print(f"Analyse: {analyse}\n")
    
    # Génération
    prompt = generer_meta_prompt(objectif)
    print("PROMPT GÉNÉRÉ:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    
    # Vérifications
    assert "email" in prompt.lower(), "Le mot 'email' devrait être dans le prompt"
    assert "JSON" in prompt or "json" in prompt, "Le format JSON devrait être mentionné"
    assert "RÔLE" in prompt, "La section RÔLE devrait être présente"
    assert "TÂCHE" in prompt, "La section TÂCHE devrait être présente"
    
    print("\n✅ Test extraction email : OK\n")


def test_extraction_avec_securite():
    """Test : les guardrails de sécurité sont ajoutés"""
    print("=" * 80)
    print("TEST 2: Extraction avec sécurité")
    print("=" * 80)
    
    objectif = "Extrais des noms de personnes avec protection des données personnelles"
    print(f"\nObjectif: {objectif}\n")
    
    analyse = _parse_goal(objectif)
    print(f"Analyse: {analyse}\n")
    
    prompt = generer_meta_prompt(objectif)
    print("PROMPT GÉNÉRÉ:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    
    # Vérifications
    assert analyse['security'] == True, "La sécurité devrait être détectée"
    assert any(mot in prompt.lower() for mot in ['sécurité', 'securite', 'confidentiel', 'rgpd']), \
        "Les guardrails de sécurité devraient être présents"
    
    print("\n✅ Test sécurité : OK\n")


def test_classification_json():
    """Test : classification avec format JSON"""
    print("=" * 80)
    print("TEST 3: Classification en JSON")
    print("=" * 80)
    
    objectif = "Créer un prompt pour classifier des emails en spam/non-spam en JSON"
    print(f"\nObjectif: {objectif}\n")
    
    analyse = _parse_goal(objectif)
    print(f"Analyse: {analyse}\n")
    
    prompt = generer_meta_prompt(objectif)
    print("PROMPT GÉNÉRÉ:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    
    # Vérifications
    assert analyse['task'] == 'classification', f"Tâche devrait être 'classification', got {analyse['task']}"
    assert analyse['format'] == 'json', f"Format devrait être 'json', got {analyse['format']}"
    assert "classification" in prompt.lower(), "Le mot 'classification' devrait être dans le prompt"
    
    print("\n✅ Test classification JSON : OK\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTS META-PROMPTING ARCHITECT")
    print("=" * 80 + "\n")
    
    try:
        test_extraction_email()
        test_extraction_avec_securite()
        test_classification_json()
        
        print("\n" + "=" * 80)
        print("🎉 TOUS LES TESTS PASSENT !")
        print("=" * 80 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
