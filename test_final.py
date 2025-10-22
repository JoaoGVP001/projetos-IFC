#!/usr/bin/env python3
import requests
import json

def test_register():
    url = "http://localhost:8000/api/v1/auth/register"
    data = {
        "username": "finaltestuser",
        "email": "finaltest@example.com",
        "password": "finaltestpass123",
        "full_name": "Final Test User"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 201:
            print("SUCCESS: Registro bem-sucedido!")
            return True
        else:
            print("ERROR: Falha no registro")
            return False

    except requests.exceptions.ConnectionError:
        print("ERROR: Erro de conexão - servidor não está rodando")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_register()
