from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.character_item import CharacterItem
from app.schemas.item import ItemCreate, ItemUpdate, CharacterItemCreate, CharacterItemUpdate


class ItemService:
    @staticmethod
    def create_item(db: Session, item: ItemCreate) -> Item:
        """Create a new item"""
        db_item = Item(**item.dict())
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def get_item(db: Session, item_id: int) -> Optional[Item]:
        """Get item by ID"""
        return db.query(Item).filter(Item.id == item_id).first()

    @staticmethod
    def get_items_by_type(db: Session, item_type: str, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get items by type"""
        return db.query(Item).filter(Item.item_type == item_type).offset(skip).limit(limit).all()

    @staticmethod
    def get_items_by_rarity(db: Session, rarity: str, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get items by rarity"""
        return db.query(Item).filter(Item.rarity == rarity).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get all items with pagination"""
        return db.query(Item).offset(skip).limit(limit).all()

    @staticmethod
    def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Update item"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            return None
        
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        """Delete item"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        return True

    @staticmethod
    def add_item_to_character(db: Session, character_id: int, character_item: CharacterItemCreate) -> Optional[CharacterItem]:
        """Add item to character"""
        db_character_item = CharacterItem(
            character_id=character_id,
            item_id=character_item.item_id,
            quantity=character_item.quantity,
            is_equipped=character_item.is_equipped
        )
        
        db.add(db_character_item)
        db.commit()
        db.refresh(db_character_item)
        return db_character_item

    @staticmethod
    def get_character_items(db: Session, character_id: int) -> List[CharacterItem]:
        """Get all items for a character"""
        return db.query(CharacterItem).filter(CharacterItem.character_id == character_id).all()

    @staticmethod
    def update_character_item(db: Session, character_item_id: int, item_update: CharacterItemUpdate) -> Optional[CharacterItem]:
        """Update character item"""
        db_character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
        if not db_character_item:
            return None
        
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_character_item, field, value)
        
        db.commit()
        db.refresh(db_character_item)
        return db_character_item

    @staticmethod
    def remove_item_from_character(db: Session, character_item_id: int) -> bool:
        """Remove item from character"""
        db_character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
        if not db_character_item:
            return False
        
        db.delete(db_character_item)
        db.commit()
        return True

    @staticmethod
    def equip_item(db: Session, character_item_id: int) -> Optional[CharacterItem]:
        """Equip an item"""
        db_character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
        if not db_character_item:
            return None
        
        db_character_item.is_equipped = True
        db.commit()
        db.refresh(db_character_item)
        return db_character_item

    @staticmethod
    def unequip_item(db: Session, character_item_id: int) -> Optional[CharacterItem]:
        """Unequip an item"""
        db_character_item = db.query(CharacterItem).filter(CharacterItem.id == character_item_id).first()
        if not db_character_item:
            return None
        
        db_character_item.is_equipped = False
        db.commit()
        db.refresh(db_character_item)
        return db_character_item
