from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    system: str = "Sigil RPG"
    max_players: int = 6
    is_active: bool = True
    is_public: bool = False
    setting: Optional[str] = None
    rules: Optional[str] = None
    notes: Optional[str] = None
    master_name: str


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system: Optional[str] = None
    max_players: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    setting: Optional[str] = None
    rules: Optional[str] = None
    notes: Optional[str] = None
    master_name: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True