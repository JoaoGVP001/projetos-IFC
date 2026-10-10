#!/usr/bin/env python3
"""
Script para testar a API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=data)
        print(f"✅ Register: {response.status_code}")
        if response.status_code == 201:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Register failed: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Token: {token_data.get('access_token', 'N/A')[:20]}...")
            return token_data.get('access_token')
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_create_character(token):
    """Test character creation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": "Alex Silva",
            "player_name": "Test User",
            "origin": "Cultista",
            "character_class": "Ocultista",
            "nex": 15,
            "agilidade": 2,
            "intelecto": 3,
            "vigor": 1,
            "presenca": 2,
            "forca": 1
        }
        response = requests.post(f"{BASE_URL}/api/v1/characters", json=data, headers=headers)
        print(f"✅ Create Character: {response.status_code}")
        if response.status_code == 201:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create Character failed: {e}")
        return False

def test_get_characters(token):
    """Test get characters"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/characters", headers=headers)
        print(f"✅ Get Characters: {response.status_code}")
        if response.status_code == 200:
            characters = response.json()
            print(f"Found {len(characters)} characters")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Characters failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Sigil RPG API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ API is not running. Please start the server first.")
        return
    
    print("\n" + "=" * 50)
    
    # Test registration
    test_register()
    
    print("\n" + "=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed, cannot continue with authenticated tests")
        return
    
    print("\n" + "=" * 50)
    
    # Test character creation
    test_create_character(token)
    
    print("\n" + "=" * 50)
    
    # Test get characters
    test_get_characters(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
