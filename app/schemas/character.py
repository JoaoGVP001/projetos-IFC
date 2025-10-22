from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class CharacterBase(BaseModel):
    name: str
    player_name: str
    origin: str
    character_class: str
    nex: int = 5
    avatar_url: Optional[str] = None
    agilidade: int = 1
    intelecto: int = 1
    vigor: int = 1
    presenca: int = 1
    forca: int = 1
    gender: Optional[str] = None
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    objective: Optional[str] = None

    @validator('nex')
    def nex_must_be_valid(cls, v):
        if not 5 <= v <= 100:
            raise ValueError('NEX must be between 5 and 100')
        return v

    @validator('agilidade', 'intelecto', 'vigor', 'presenca', 'forca')
    def attributes_must_be_valid(cls, v):
        if not 0 <= v <= 3:
            raise ValueError('Attributes must be between 0 and 3')
        return v


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    player_name: Optional[str] = None
    origin: Optional[str] = None
    character_class: Optional[str] = None
    nex: Optional[int] = None
    avatar_url: Optional[str] = None
    agilidade: Optional[int] = None
    intelecto: Optional[int] = None
    vigor: Optional[int] = None
    presenca: Optional[int] = None
    forca: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    objective: Optional[str] = None

    @validator('nex')
    def nex_must_be_valid(cls, v):
        if v is not None and not 5 <= v <= 100:
            raise ValueError('NEX must be between 5 and 100')
        return v

    @validator('agilidade', 'intelecto', 'vigor', 'presenca', 'forca')
    def attributes_must_be_valid(cls, v):
        if v is not None and not 0 <= v <= 3:
            raise ValueError('Attributes must be between 0 and 3')
        return v


class CharacterResponse(CharacterBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True