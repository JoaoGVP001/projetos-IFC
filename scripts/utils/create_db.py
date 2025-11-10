#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da API Flask
"""
import sys
import os

# Add the API directory to the Python path
api_path = os.path.join(os.path.dirname(__file__), '..', '..', 'SigilRPG_API-main')
sys.path.insert(0, api_path)
os.chdir(api_path)

from app import app
from models import db

def create_tables():
    """Create all database tables"""
    print("📦 Criando tabelas do banco de dados...")
    with app.app_context():
        db.create_all()
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()
