from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.character import CharacterCreate, CharacterOut

router = APIRouter()

# In-memory store (placeholder until DB wiring)
_characters: List[CharacterOut] = []

@router.get("/", response_model=List[CharacterOut])
async def list_characters():
    return _characters

@router.post("/", response_model=CharacterOut, status_code=201)
async def create_character(payload: CharacterCreate):
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
    for c in _characters:
        if c.id == character_id:
            return c
    raise HTTPException(status_code=404, detail="Character not found")

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.auth_service import AuthService
from app.services.character_service import CharacterService
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse, CharacterWithUser, CharacterWithCampaign
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: CharacterCreate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new character"""
    return CharacterService.create_character(db=db, character=character, user_id=current_user.id)


@router.get("/", response_model=List[CharacterResponse])
async def get_characters(
    skip: int = 0,
    limit: int = 100,
    campaign_id: int = None,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get characters"""
    if campaign_id:
        return CharacterService.get_characters_by_campaign(db=db, campaign_id=campaign_id, skip=skip, limit=limit)
    else:
        # Users can only see their own characters unless they're admin
        if current_user.is_admin:
            return CharacterService.get_all_characters(db=db, skip=skip, limit=limit)
        else:
            return CharacterService.get_characters_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/my", response_model=List[CharacterResponse])
async def get_my_characters(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's characters"""
    return CharacterService.get_characters_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{character_id}", response_model=CharacterWithUser)
async def get_character(
    character_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get character by ID"""
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Users can only view their own characters unless they're admin
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update character"""
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Users can only update their own characters unless they're admin
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return CharacterService.update_character(db=db, character_id=character_id, character_update=character_update)


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete character"""
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Users can only delete their own characters unless they're admin
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = CharacterService.delete_character(db=db, character_id=character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {"message": "Character deleted successfully"}


@router.post("/{character_id}/campaign/{campaign_id}")
async def add_character_to_campaign(
    character_id: int,
    campaign_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add character to campaign"""
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Users can only add their own characters to campaigns unless they're admin
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_character = CharacterService.add_character_to_campaign(db=db, character_id=character_id, campaign_id=campaign_id)
    if updated_character is None:
        raise HTTPException(status_code=400, detail="Failed to add character to campaign")
    
    return {"message": "Character added to campaign successfully"}


@router.delete("/{character_id}/campaign")
async def remove_character_from_campaign(
    character_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove character from campaign"""
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Users can only remove their own characters from campaigns unless they're admin
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_character = CharacterService.remove_character_from_campaign(db=db, character_id=character_id)
    if updated_character is None:
        raise HTTPException(status_code=400, detail="Failed to remove character from campaign")
    
    return {"message": "Character removed from campaign successfully"}
