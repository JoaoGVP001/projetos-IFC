#!/usr/bin/env python3
"""
Script de teste para verificar a integração entre Flask e Flutter
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Testa a conexão com a API"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("API Flask esta rodando")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"API retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Nao foi possivel conectar a API Flask")
        print("Certifique-se de que a API esta rodando na porta 8000")
        return False

def test_characters_endpoint():
    """Testa o endpoint de personagens"""
    try:
        response = requests.get(f"{BASE_URL}/api/characters")
        if response.status_code == 200:
            print("Endpoint de personagens funcionando")
            characters = response.json()
            print(f"Encontrados {len(characters)} personagens")
            return True
        else:
            print(f"Endpoint de personagens retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao testar endpoint de personagens: {e}")
        return False

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
        
        response = requests.post(
            f"{BASE_URL}/api/characters",
            json=character_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("Criacao de personagem funcionando")
            character = response.json()
            print(f"Personagem criado: {character['name']} (ID: {character['id']})")
            return character['id']
        else:
            print(f"Criacao de personagem retornou status {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao criar personagem: {e}")
        return None

def test_cors_headers():
    """Testa se os headers CORS estão configurados"""
    try:
        response = requests.options(f"{BASE_URL}/api/characters")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("Headers CORS configurados")
            print(f"CORS Headers: {cors_headers}")
            return True
        else:
            print("Headers CORS nao encontrados")
            return False
    except Exception as e:
        print(f"Erro ao testar CORS: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("Testando integracao Flask-Flutter...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Conexão com API
    if test_api_connection():
        tests_passed += 1
    
    print()
    
    # Teste 2: Headers CORS
    if test_cors_headers():
        tests_passed += 1
    
    print()
    
    # Teste 3: Endpoint de personagens
    if test_characters_endpoint():
        tests_passed += 1
    
    print()
    
    # Teste 4: Criação de personagem
    character_id = test_create_character()
    if character_id:
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"Resultado: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("Todos os testes passaram! A integracao esta funcionando.")
        print("\nProximos passos:")
        print("1. Execute o app Flutter")
        print("2. Teste a criacao de personagens")
        print("3. Teste a autenticacao (se implementada)")
    else:
        print("Alguns testes falharam. Verifique a configuracao da API.")

if __name__ == "__main__":
    main()
