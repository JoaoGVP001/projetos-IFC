"""
Script de teste para a API Flask RPG
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Testa os endpoints principais da API"""
    
    print("🧪 Testando API Flask RPG...")
    print("=" * 50)
    
    # Teste 1: Endpoint raiz
    print("\n1. Testando endpoint raiz...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Teste 2: Listar personagens
    print("\n2. Testando listagem de personagens...")
    try:
        response = requests.get(f"{BASE_URL}/api/characters")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Personagens encontrados: {len(data['data'])}")
            if data['data']:
                print(f"Primeiro personagem: {data['data'][0]['name']}")
        else:
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Teste 3: Login
    print("\n3. Testando login...")
    try:
        login_data = {
            "email": "joao@example.com",
            "password": "123456"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data['data']['token']
            print(f"Token obtido: {token[:20]}...")
            
            # Teste 4: Ver usuário autenticado
            print("\n4. Testando usuário autenticado...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/auth/user", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"Usuário: {user_data['data']['name']}")
            
            # Teste 5: Ver personagem do usuário
            print("\n5. Testando personagem do usuário...")
            response = requests.get(f"{BASE_URL}/api/me/", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                char_data = response.json()
                print(f"Personagem: {char_data['data']['name']}")
            
            # Teste 6: Listar lutas do usuário
            print("\n6. Testando lutas do usuário...")
            response = requests.get(f"{BASE_URL}/api/me/fights/", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                fights_data = response.json()
                print(f"Lutas encontradas: {len(fights_data['data'])}")
            
            # Teste 7: Criar nova luta
            print("\n7. Testando criação de luta...")
            fight_data = {"opponent_id": 3}  # Assumindo que existe um personagem com ID 3
            response = requests.post(f"{BASE_URL}/api/me/fights/", json=fight_data, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                fight_result = response.json()
                print(f"Luta criada: Status {fight_result['data']['status']}, XP: {fight_result['data']['experience']}")
            
        else:
            print(f"Erro no login: {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    test_api()


