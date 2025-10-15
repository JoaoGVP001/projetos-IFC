from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(user.password)
        
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """Get user statistics"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        characters_count = db.query(func.count(User.characters)).filter(User.id == user_id).scalar() or 0
        campaigns_master_count = db.query(func.count(User.campaigns_as_master)).filter(User.id == user_id).scalar() or 0
        campaigns_player_count = db.query(func.count(User.campaigns_as_player)).filter(User.id == user_id).scalar() or 0
        
        return {
            "characters_count": characters_count,
            "campaigns_master_count": campaigns_master_count,
            "campaigns_player_count": campaigns_player_count
        }


# Import AuthService here to avoid circular import
from app.services.auth_service import AuthService
