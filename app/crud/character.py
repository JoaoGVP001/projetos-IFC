from sqlalchemy.orm import Session
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate
from typing import List, Optional


class CharacterService:
    @staticmethod
    def get_character_by_id(db: Session, character_id: int) -> Optional[Character]:
        return db.query(Character).filter(Character.id == character_id).first()

    @staticmethod
    def get_characters_by_user(db: Session, user_id: int) -> List[Character]:
        return db.query(Character).filter(Character.user_id == user_id).all()

    @staticmethod
    def create_character(db: Session, character: CharacterCreate, user_id: int) -> Character:
        db_character = Character(
            **character.dict(),
            user_id=user_id
        )
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character

    @staticmethod
    def update_character(db: Session, character_id: int, character_update: CharacterUpdate) -> Optional[Character]:
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
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if not db_character:
            return False
        
        db.delete(db_character)
        db.commit()
        return True
