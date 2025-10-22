#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base, get_db
from app.models import User, Character, Campaign, Item, CharacterItem
from sqlalchemy.orm import Session

def test_database():
    try:
        # Test database connection
        print("Testing database connection...")
        db = next(get_db())
        
        # Test creating tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Test querying User table
        print("Testing User table...")
        users = db.query(User).all()
        print(f"Found {len(users)} users")
        
        # Test creating a user
        print("Testing user creation...")
        from app.crud.user import UserService
        from app.schemas.user import UserCreate
        
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            full_name="Test User"
        )
        
        user = UserService.create_user(db, user_data)
        print(f"Created user: {user.username}")
        
        print("Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_database()
