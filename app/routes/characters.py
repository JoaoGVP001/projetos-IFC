from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from app.services.auth_service import AuthService
from app.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate

router = APIRouter()

# In-memory store (placeholder until DB wiring)
_characters: List[CharacterOut] = []

@router.get("/", response_model=List[CharacterOut])
async def list_characters():
    """Get all PUBLIC characters"""
    return [c for c in _characters if getattr(c, 'public', True)]


@router.get("/mine", response_model=List[CharacterOut])
async def list_my_characters(current_user = Depends(AuthService.get_current_active_user)):
    """Get characters owned by the current user"""
    return [c for c in _characters if getattr(c, 'owner', None) == current_user.username]

@router.post("/", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
async def create_character(payload: CharacterCreate, current_user = Depends(AuthService.get_current_active_user)):
    """Create a new character (owned by current user)"""
    new = CharacterOut(
        id=str(len(_characters) + 1),
        name=payload.name,
        playerName=payload.playerName,
        origin=payload.origin,
        characterClass=payload.characterClass,
        nex=payload.nex,
        avatarUrl=payload.avatarUrl,
        public=payload.public,
        owner=current_user.username,
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


@router.patch("/{character_id}", response_model=CharacterOut)
async def update_character(character_id: str, payload: CharacterUpdate, current_user = Depends(AuthService.get_current_active_user)):
    """Partially update a character"""
    for i, c in enumerate(_characters):
        if c.id == character_id:
            if getattr(c, 'owner', None) != current_user.username:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not owner")
            data = c.dict()
            updates = payload.dict(exclude_unset=True)
            data.update({k: v for k, v in updates.items() if v is not None})
            updated = CharacterOut(**data)
            _characters[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Character not found")
