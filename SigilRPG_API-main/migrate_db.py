#!/usr/bin/env python3
"""
Script para migrar o banco de dados existente para a nova estrutura
"""

import sqlite3
import os

def migrate_database():
    """Migra o banco de dados para a nova estrutura"""
    
    # Caminho do banco de dados
    db_path = 'instance/rpg.db'
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado. Execute primeiro a API Flask para criar o banco.")
        return
    
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se as novas colunas já existem
        cursor.execute("PRAGMA table_info(characters)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Adicionar novas colunas se não existirem
        new_columns = [
            ('player_name', 'VARCHAR(255)'),
            ('character_class', 'VARCHAR(255)'),
            ('nex', 'INTEGER DEFAULT 0'),
            ('avatar_url', 'VARCHAR(500)'),
            ('agilidade', 'INTEGER DEFAULT 1'),
            ('intelecto', 'INTEGER DEFAULT 1'),
            ('vigor', 'INTEGER DEFAULT 1'),
            ('presenca', 'INTEGER DEFAULT 1'),
            ('forca', 'INTEGER DEFAULT 1'),
            ('gender', 'VARCHAR(50)'),
            ('appearance', 'TEXT'),
            ('personality', 'TEXT'),
            ('background', 'TEXT'),
            ('objective', 'TEXT'),
            ('origin', 'VARCHAR(255)'),
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE characters ADD COLUMN {column_name} {column_type}")
                    print(f"Adicionada coluna: {column_name}")
                except sqlite3.Error as e:
                    print(f"Erro ao adicionar coluna {column_name}: {e}")
        
        # Atualizar valores padrão para personagens existentes
        cursor.execute("""
            UPDATE characters 
            SET agilidade = 1, intelecto = 1, vigor = 1, presenca = 1, forca = 1, nex = 0
            WHERE agilidade IS NULL OR intelecto IS NULL OR vigor IS NULL OR presenca IS NULL OR forca IS NULL OR nex IS NULL
        """)
        
        conn.commit()
        print("Migração concluída com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
