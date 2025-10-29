#!/usr/bin/env python3
"""
Script simples para testar se a API Flask está funcionando
"""

from app import app

if __name__ == '__main__':
    print("Iniciando API Flask...")
    try:
        app.run(debug=True, host='0.0.0.0', port=8000)
    except Exception as e:
        print(f"Erro ao iniciar API: {e}")
