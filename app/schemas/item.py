from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    item_type: str
    rarity: str = "common"
    
    # Estatísticas do item
    weight: float = 0.0
    value: int = 0
    quantity: int = 1
    
    # Propriedades específicas
    is_magical: bool = False
    is_consumable: bool = False
    is_equippable: bool = True
    
    # Dados em JSON para propriedades específicas
    properties: Optional[Dict[str, Any]] = {}

    @validator('item_type')
    def item_type_must_be_valid(cls, v):
        valid_types = ['weapon', 'armor', 'consumable', 'tool', 'miscellaneous', 'spell', 'book']
        if v not in valid_types:
            raise ValueError(f'Item type must be one of: {", ".join(valid_types)}')
        return v

    @validator('rarity')
    def rarity_must_be_valid(cls, v):
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        if v not in valid_rarities:
            raise ValueError(f'Rarity must be one of: {", ".join(valid_rarities)}')
        return v

    @validator('weight', 'value')
    def numeric_values_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Weight and value must be non-negative')
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    rarity: Optional[str] = None
    weight: Optional[float] = None
    value: Optional[int] = None
    quantity: Optional[int] = None
    is_magical: Optional[bool] = None
    is_consumable: Optional[bool] = None
    is_equippable: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CharacterItemCreate(BaseModel):
    item_id: int
    quantity: int = 1
    is_equipped: bool = False


class CharacterItemUpdate(BaseModel):
    quantity: Optional[int] = None
    is_equipped: Optional[bool] = None


class CharacterItemResponse(BaseModel):
    id: int
    character_id: int
    item_id: int
    quantity: int
    is_equipped: bool
    item: ItemResponse
    created_at: datetime

    class Config:
        from_attributes = True
