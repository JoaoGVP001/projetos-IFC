#!/usr/bin/env python3
"""
Script de migração para adicionar campos de combate (current_pv, current_pe, current_ps)
"""
import sqlite3
import os
import sys

def migrate_database():
    """Adiciona colunas de combate à tabela characters"""
    
    # Caminho do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'rpg.db')
    
    # Se não existir, tenta na raiz
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), 'rpg.db')
    
    if not os.path.exists(db_path):
        print(f"[ERRO] Banco de dados nao encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(characters)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        # Adicionar current_pv se não existir
        if 'current_pv' not in columns:
            print("[+] Adicionando coluna current_pv...")
            cursor.execute("ALTER TABLE characters ADD COLUMN current_pv INTEGER")
            changes_made = True
        
        # Adicionar current_pe se não existir
        if 'current_pe' not in columns:
            print("[+] Adicionando coluna current_pe...")
            cursor.execute("ALTER TABLE characters ADD COLUMN current_pe INTEGER")
            changes_made = True
        
        # Adicionar current_ps se não existir
        if 'current_ps' not in columns:
            print("[+] Adicionando coluna current_ps...")
            cursor.execute("ALTER TABLE characters ADD COLUMN current_ps INTEGER")
            changes_made = True
        
        if changes_made:
            # Inicializar valores para personagens existentes
            print("[*] Inicializando valores de combate para personagens existentes...")
            
            # Buscar todos os personagens
            cursor.execute("SELECT id, vigor, forca, intelecto, presenca FROM characters")
            characters = cursor.fetchall()
            
            for char_id, vigor, forca, intelecto, presenca in characters:
                # Calcular valores máximos
                max_pv = 10 + (vigor * 5) + (forca * 2)
                max_pe = 6 + (intelecto * 4) + (presenca * 2)
                max_ps = 8 + (intelecto * 3) + (presenca * 3)
                
                # Atualizar apenas se os valores estiverem NULL
                cursor.execute("""
                    UPDATE characters 
                    SET current_pv = COALESCE(current_pv, ?),
                        current_pe = COALESCE(current_pe, ?),
                        current_ps = COALESCE(current_ps, ?)
                    WHERE id = ?
                """, (max_pv, max_pe, max_ps, char_id))
            
            print(f"[OK] {len(characters)} personagens atualizados")
        else:
            print("[OK] Todas as colunas ja existem")
        
        conn.commit()
        conn.close()
        
        print("[OK] Migracao concluida com sucesso!")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro na migracao: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)

