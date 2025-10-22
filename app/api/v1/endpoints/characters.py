from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse

router = APIRouter()


@router.get("/", response_model=List[CharacterResponse])
async def get_characters(db: Session = Depends(get_db)):
    """Get all characters"""
    characters = db.query(Character).all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a specific character by ID"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    return character


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    db_character = Character(
        name=character.name,
        player_name=character.player_name,
        origin=character.origin,
        character_class=character.character_class,
        nex=character.nex,
        avatar_url=character.avatar_url,
        agilidade=character.agilidade,
        intelecto=character.intelecto,
        vigor=character.vigor,
        presenca=character.presenca,
        forca=character.forca,
        gender=character.gender,
        age=character.age,
        appearance=character.appearance,
        personality=character.personality,
        background=character.background,
        objective=character.objective,
    )
    
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
    return db_character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)):
    """Update a character"""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    for field, value in character.dict().items():
        if value is not None:
            setattr(db_character, field, value)
    
    db.commit()
    db.refresh(db_character)
    
    return db_character


@router.delete("/{character_id}")
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    db.delete(character)
    db.commit()
    
    return {"message": "Character deleted successfully"}
