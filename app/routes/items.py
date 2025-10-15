from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.auth_service import AuthService
from app.services.item_service import ItemService
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, CharacterItemCreate, CharacterItemUpdate, CharacterItemResponse
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new item (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ItemService.create_item(db=db, item=item)


@router.get("/", response_model=List[ItemResponse])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    item_type: str = None,
    rarity: str = None,
    db: Session = Depends(get_db)
):
    """Get items with optional filters"""
    if item_type:
        return ItemService.get_items_by_type(db=db, item_type=item_type, skip=skip, limit=limit)
    elif rarity:
        return ItemService.get_items_by_rarity(db=db, rarity=rarity, skip=skip, limit=limit)
    else:
        return ItemService.get_all_items(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get item by ID"""
    item = ItemService.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update item (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    item = ItemService.update_item(db=db, item_id=item_id, item_update=item_update)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete item (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = ItemService.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted successfully"}


@router.post("/characters/{character_id}/items", response_model=CharacterItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_character(
    character_id: int,
    character_item: CharacterItemCreate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add item to character"""
    # Verify character belongs to user or user is admin
    from app.services.character_service import CharacterService
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ItemService.add_item_to_character(db=db, character_id=character_id, character_item=character_item)


@router.get("/characters/{character_id}/items", response_model=List[CharacterItemResponse])
async def get_character_items(
    character_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get character items"""
    # Verify character belongs to user or user is admin
    from app.services.character_service import CharacterService
    character = CharacterService.get_character(db=db, character_id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return ItemService.get_character_items(db=db, character_id=character_id)


@router.put("/character-items/{character_item_id}", response_model=CharacterItemResponse)
async def update_character_item(
    character_item_id: int,
    item_update: CharacterItemUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update character item"""
    # Verify character item belongs to user or user is admin
    from app.models.character_item import CharacterItem
    character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
    if character_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    character = db.query(Character).filter(Character.id == character_item.character_id).first()
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_item = ItemService.update_character_item(db=db, character_item_id=character_item_id, item_update=item_update)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    return updated_item


@router.delete("/character-items/{character_item_id}")
async def remove_item_from_character(
    character_item_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove item from character"""
    # Verify character item belongs to user or user is admin
    from app.models.character_item import CharacterItem
    from app.models.character import Character
    
    character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
    if character_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    character = db.query(Character).filter(Character.id == character_item.character_id).first()
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = ItemService.remove_item_from_character(db=db, character_item_id=character_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    return {"message": "Item removed from character successfully"}


@router.post("/character-items/{character_item_id}/equip")
async def equip_item(
    character_item_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Equip an item"""
    # Verify character item belongs to user or user is admin
    from app.models.character_item import CharacterItem
    from app.models.character import Character
    
    character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
    if character_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    character = db.query(Character).filter(Character.id == character_item.character_id).first()
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_item = ItemService.equip_item(db=db, character_item_id=character_item_id)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    return {"message": "Item equipped successfully"}


@router.post("/character-items/{character_item_id}/unequip")
async def unequip_item(
    character_item_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unequip an item"""
    # Verify character item belongs to user or user is admin
    from app.models.character_item import CharacterItem
    from app.models.character import Character
    
    character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
    if character_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    character = db.query(Character).filter(Character.id == character_item.character_id).first()
    if character.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_item = ItemService.unequip_item(db=db, character_item_id=character_item_id)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Character item not found")
    
    return {"message": "Item unequipped successfully"}
