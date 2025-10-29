#!/usr/bin/env python3
"""
Script de teste para o sistema de login completo (versão limpa)
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Testa o login de um usuário"""
    try:
        login_data = {
            "email": "joao@teste.com",
            "password": "123456"
        }
        
        print("Testando login de usuário...")
        print(f"Dados: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCESSO: Login realizado!")
            data = response.json()
            token = data['data']['token']
            print(f"Token: {token[:20]}...")
            return token
        else:
            print(f"ERRO: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERRO: {e}")
        return None

def test_get_user(token):
    """Testa a obtenção de dados do usuário autenticado"""
    try:
        print(f"\nTestando obtenção de dados do usuário...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/auth/user",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCESSO: Dados do usuário obtidos!")
            data = response.json()
            user = data['data']
            print(f"Usuário: {user['name']} ({user['email']})")
            return True
        else:
            print(f"ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_create_character_with_auth(token):
    """Testa a criação de personagem com autenticação"""
    try:
        print(f"\nTestando criação de personagem com autenticação...")
        
        character_data = {
            "name": "Legolas",
            "player_name": "João Silva",
            "age": 2000,
            "skilled_in": "Arco e Flechas",
            "character_class": "Arqueiro",
            "nex": 7,
            "agilidade": 5,
            "intelecto": 3,
            "vigor": 3,
            "presenca": 4,
            "forca": 2,
            "gender": "Masculino",
            "origin": "Mirkwood"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/characters",
            json=character_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("SUCESSO: Personagem criado com autenticação!")
            character = response.json()
            print(f"Personagem: {character['name']} (ID: {character['id']})")
            return True
        else:
            print(f"ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_logout(token):
    """Testa o logout"""
    try:
        print(f"\nTestando logout...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(
            f"{BASE_URL}/api/auth/",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCESSO: Logout realizado!")
            return True
        else:
            print(f"ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Executa todos os testes do sistema de login"""
    print("Testando sistema completo de login...")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Login
    token = test_login()
    if token:
        tests_passed += 1
    
    # Teste 2: Obter dados do usuário
    if token:
        if test_get_user(token):
            tests_passed += 1
    
    # Teste 3: Criar personagem com autenticação
    if token:
        if test_create_character_with_auth(token):
            tests_passed += 1
    
    # Teste 4: Logout
    if token:
        if test_logout(token):
            tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Resultado: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("Sistema de login funcionando perfeitamente!")
        print("\nPróximos passos:")
        print("1. Execute o app Flutter")
        print("2. Teste o login")
        print("3. Teste a criação de personagens autenticada")
    else:
        print("Alguns testes falharam. Verifique a configuração.")

if __name__ == "__main__":
    main()
