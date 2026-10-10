#!/usr/bin/env python3
"""
Script para executar o servidor Flask de desenvolvimento
"""
import sys
import os

# Add the API directory to the Python path
# Go up two levels from scripts/utils/ to reach root, then into SigilRPG_API-main
api_path = os.path.join(os.path.dirname(__file__), '..', '..', 'SigilRPG_API-main')
sys.path.insert(0, api_path)
os.chdir(api_path)  # Change to API directory

# Import and run Flask app
from app import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask na porta 8000...")
    print(f"📁 Diretório: {api_path}")
    app.run(debug=True, host='0.0.0.0', port=8000)
