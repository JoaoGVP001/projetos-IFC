from pydantic import BaseModel, Field
from typing import Optional


class CharacterBase(BaseModel):
    name: str = Field(min_length=1)
    playerName: str = Field(min_length=1)
    origin: str
    characterClass: str
    nex: int = Field(ge=0, le=100)
    avatarUrl: Optional[str] = None
    public: bool = True
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
    owner: Optional[str] = None

    class Config:
        from_attributes = True


class CharacterUpdate(BaseModel):
    # all fields optional for partial updates
    name: Optional[str] = None
    playerName: Optional[str] = None
    origin: Optional[str] = None
    characterClass: Optional[str] = None
    nex: Optional[int] = Field(default=None, ge=0, le=100)
    avatarUrl: Optional[str] = None
    public: Optional[bool] = None
    agilidade: Optional[int] = Field(default=None, ge=0, le=3)
    intelecto: Optional[int] = Field(default=None, ge=0, le=3)
    vigor: Optional[int] = Field(default=None, ge=0, le=3)
    presenca: Optional[int] = Field(default=None, ge=0, le=3)
    forca: Optional[int] = Field(default=None, ge=0, le=3)
    gender: Optional[str] = None
    age: Optional[int] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    objective: Optional[str] = None

