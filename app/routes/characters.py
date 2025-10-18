from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.character import CharacterCreate, CharacterOut

router = APIRouter()

# In-memory store (placeholder until DB wiring)
_characters: List[CharacterOut] = []

@router.get("/", response_model=List[CharacterOut])
async def list_characters():
    """Get all characters"""
    return _characters

@router.post("/", response_model=CharacterOut, status_code=201)
async def create_character(payload: CharacterCreate):
    """Create a new character"""
    new = CharacterOut(
        id=str(len(_characters) + 1),
        name=payload.name,
        playerName=payload.playerName,
        origin=payload.origin,
        characterClass=payload.characterClass,
        nex=payload.nex,
        avatarUrl=payload.avatarUrl,
    )
    _characters.append(new)
    return new

@router.get("/{character_id}", response_model=CharacterOut)
async def get_character(character_id: str):
    """Get character by ID"""
    for c in _characters:
        if c.id == character_id:
            return c
    raise HTTPException(status_code=404, detail="Character not found")
