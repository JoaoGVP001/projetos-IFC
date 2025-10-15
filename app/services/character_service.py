from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate


class CharacterService:
    @staticmethod
    def create_character(db: Session, character: CharacterCreate, user_id: int) -> Character:
        """Create a new character"""
        db_character = Character(
            **character.dict(),
            user_id=user_id
        )
        
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character

    @staticmethod
    def get_character(db: Session, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        return db.query(Character).filter(Character.id == character_id).first()

    @staticmethod
    def get_characters_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Character]:
        """Get characters by user ID"""
        return db.query(Character).filter(Character.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_characters_by_campaign(db: Session, campaign_id: int, skip: int = 0, limit: int = 100) -> List[Character]:
        """Get characters by campaign ID"""
        return db.query(Character).filter(Character.campaign_id == campaign_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_characters(db: Session, skip: int = 0, limit: int = 100) -> List[Character]:
        """Get all characters with pagination"""
        return db.query(Character).offset(skip).limit(limit).all()

    @staticmethod
    def update_character(db: Session, character_id: int, character_update: CharacterUpdate) -> Optional[Character]:
        """Update character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if not db_character:
            return None
        
        update_data = character_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_character, field, value)
        
        db.commit()
        db.refresh(db_character)
        return db_character

    @staticmethod
    def delete_character(db: Session, character_id: int) -> bool:
        """Delete character"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if not db_character:
            return False
        
        db.delete(db_character)
        db.commit()
        return True

    @staticmethod
    def add_character_to_campaign(db: Session, character_id: int, campaign_id: int) -> Optional[Character]:
        """Add character to campaign"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if not db_character:
            return None
        
        db_character.campaign_id = campaign_id
        db.commit()
        db.refresh(db_character)
        return db_character

    @staticmethod
    def remove_character_from_campaign(db: Session, character_id: int) -> Optional[Character]:
        """Remove character from campaign"""
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if not db_character:
            return None
        
        db_character.campaign_id = None
        db.commit()
        db.refresh(db_character)
        return db_character
