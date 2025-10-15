from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    system: str = "D&D 5e"
    max_players: int = 6
    is_active: bool = True
    is_public: bool = False
    
    # Configurações da campanha
    setting: Optional[str] = None
    rules: Optional[str] = None
    notes: Optional[str] = None

    @validator('max_players')
    def max_players_must_be_valid(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Max players must be between 1 and 12')
        return v


class CampaignCreate(CampaignBase):
    pass


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


class CampaignResponse(CampaignBase):
    id: int
    master_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignWithDetails(CampaignResponse):
    master: Optional[dict] = None
    players: List[dict] = []
    characters: List[dict] = []
    players_count: int = 0


class CampaignJoin(BaseModel):
    campaign_id: int
