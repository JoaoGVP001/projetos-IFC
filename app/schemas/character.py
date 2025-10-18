from pydantic import BaseModel, Field
from typing import Optional


class CharacterBase(BaseModel):
    name: str = Field(min_length=1)
    playerName: str = Field(min_length=1)
    origin: str
    characterClass: str
    nex: int = Field(ge=0, le=100)
    avatarUrl: Optional[str] = None
    # Atributos do personagem
    agilidade: int = Field(default=1, ge=0, le=3)
    intelecto: int = Field(default=1, ge=0, le=3)
    vigor: int = Field(default=1, ge=0, le=3)
    presenca: int = Field(default=1, ge=0, le=3)
    forca: int = Field(default=1, ge=0, le=3)
    # Detalhes do personagem
    gender: Optional[str] = None
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    objective: Optional[str] = None


class CharacterCreate(CharacterBase):
    pass


class CharacterOut(CharacterBase):
    id: str

    class Config:
        from_attributes = True

