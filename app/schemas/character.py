from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class CharacterBase(BaseModel):
    name: str = Field(min_length=1)
    playerName: str = Field(min_length=1)
    origin: str
    characterClass: str
    nex: int = Field(ge=0, le=100)
    avatarUrl: Optional[HttpUrl] = None


class CharacterCreate(CharacterBase):
    pass


class CharacterOut(CharacterBase):
    id: str

    class Config:
        from_attributes = True

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime


class CharacterBase(BaseModel):
    name: str
    class_name: str
    race: str
    level: int = 1
    experience: int = 0
    
    # Atributos básicos
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # HP e outros stats
    hit_points: int = 10
    max_hit_points: int = 10
    armor_class: int = 10
    speed: int = 30
    
    # Informações adicionais
    background: Optional[str] = None
    alignment: Optional[str] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    
    # Dados em JSON
    abilities: Optional[Dict[str, Any]] = {}
    spells: Optional[Dict[str, Any]] = {}
    equipment: Optional[Dict[str, Any]] = {}

    @validator('level')
    def level_must_be_positive(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Level must be between 1 and 20')
        return v

    @validator('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma')
    def attributes_must_be_valid(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Attributes must be between 1 and 30')
        return v


class CharacterCreate(CharacterBase):
    campaign_id: Optional[int] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    race: Optional[str] = None
    level: Optional[int] = None
    experience: Optional[int] = None
    
    # Atributos básicos
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    constitution: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None
    charisma: Optional[int] = None
    
    # HP e outros stats
    hit_points: Optional[int] = None
    max_hit_points: Optional[int] = None
    armor_class: Optional[int] = None
    speed: Optional[int] = None
    
    # Informações adicionais
    background: Optional[str] = None
    alignment: Optional[str] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    
    # Dados em JSON
    abilities: Optional[Dict[str, Any]] = None
    spells: Optional[Dict[str, Any]] = None
    equipment: Optional[Dict[str, Any]] = None


class CharacterResponse(CharacterBase):
    id: int
    user_id: int
    campaign_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CharacterWithUser(CharacterResponse):
    user: Optional[dict] = None


class CharacterWithCampaign(CharacterResponse):
    campaign: Optional[dict] = None
