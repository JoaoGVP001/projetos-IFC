#!/usr/bin/env python3
"""
Script de teste específico para criação de personagens
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_character():
    """Testa a criação de um personagem"""
    try:
        character_data = {
            "name": "Teste Personagem",
            "player_name": "Jogador Teste",
            "age": 25,
            "skilled_in": "Magia",
            "character_class": "Mago",
            "nex": 5,
            "agilidade": 2,
            "intelecto": 4,
            "vigor": 3,
            "presenca": 3,
            "forca": 1,
            "gender": "Masculino",
            "origin": "Cidade Grande"
        }
        
        print("Enviando dados para criar personagem...")
        print(f"Dados: {json.dumps(character_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/characters",
            json=character_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            allow_redirects=False  # Não seguir redirecionamentos
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("SUCESSO: Personagem criado!")
            character = response.json()
            print(f"Personagem criado: {character['name']} (ID: {character['id']})")
            return character['id']
        elif response.status_code == 308:
            print("ERRO 308: Redirecionamento permanente detectado")
            print("Location header:", response.headers.get('Location', 'N/A'))
        else:
            print(f"ERRO: Status {response.status_code}")
            
        return None
        
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def test_get_characters():
    """Testa a listagem de personagens"""
    try:
        print("\nTestando listagem de personagens...")
        response = requests.get(f"{BASE_URL}/api/characters")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            characters = response.json()
            print(f"Encontrados {len(characters)} personagens")
            return True
        else:
            print(f"ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    print("Testando criação de personagens...")
    print("=" * 50)
    
    # Teste 1: Listar personagens existentes
    test_get_characters()
    
    print("\n" + "=" * 50)
    
    # Teste 2: Criar novo personagem
    character_id = test_create_character()
    
    if character_id:
        print(f"\nPersonagem criado com sucesso! ID: {character_id}")
    else:
        print("\nFalha ao criar personagem")
