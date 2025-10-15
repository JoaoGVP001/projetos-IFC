from pydantic import BaseModel, Field
from typing import Optional


class CampaignBase(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    masterId: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignOut(CampaignBase):
    id: str

    class Config:
        from_attributes = True


