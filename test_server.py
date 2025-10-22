#!/usr/bin/env python3
"""
Script para testar se o servidor está funcionando
"""
import requests
import time
import sys

def test_server():
    """Testa se o servidor está rodando"""
    try:
        print("Testando conexao com a API...")
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("Erro: Nao foi possivel conectar ao servidor")
        print("   Verifique se o servidor esta rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("Testando servidor Sigil RPG API...")
    success = test_server()
    sys.exit(0 if success else 1)
