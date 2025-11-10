#!/usr/bin/env python3
import requests
import json

def test_campaigns():
    """Testar endpoints de campanhas"""
    base_url = "http://localhost:8000"
    
    print("=== Testando API Simplificada ===")
    
    # Testar health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check - Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API está funcionando!")
        else:
            print("❌ API com problemas")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Testar criar campanha
    try:
        campaign_data = {
            "name": "Campanha de Teste",
            "description": "Uma campanha para testar a API",
            "master_name": "Mestre Teste",
            "system": "Sigil RPG",
            "max_players": 4,
            "is_active": True,
            "is_public": True,
            "setting": "Mundo de fantasia",
            "rules": "Regras do Sigil RPG",
            "notes": "Notas do mestre"
        }
        
        response = requests.post(f"{base_url}/api/v1/campaigns/", json=campaign_data)
        print(f"\nCriar Campanha - Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Campanha criada com sucesso!")
            campaign = response.json()
            campaign_id = campaign['id']
            print(f"ID da campanha: {campaign_id}")
            
            # Testar listar campanhas
            response = requests.get(f"{base_url}/api/v1/campaigns/")
            print(f"\nListar Campanhas - Status: {response.status_code}")
            if response.status_code == 200:
                campaigns = response.json()
                print(f"✅ Encontradas {len(campaigns)} campanhas")
                
                # Testar obter campanha específica
                response = requests.get(f"{base_url}/api/v1/campaigns/{campaign_id}")
                print(f"\nObter Campanha - Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Campanha obtida com sucesso!")
                    return True
                else:
                    print("❌ Erro ao obter campanha")
                    return False
            else:
                print("❌ Erro ao listar campanhas")
                return False
        else:
            print(f"❌ Erro ao criar campanha: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_campaigns()
