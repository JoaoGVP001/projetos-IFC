#!/usr/bin/env python3
"""
Script de teste simples para verificar se a API está funcionando
"""

import requests
import time

def test_simple():
    """Teste simples de conexão"""
    try:
        print("Testando conexão com a API...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("Não foi possível conectar à API")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("Aguardando API inicializar...")
    time.sleep(3)
    test_simple()
