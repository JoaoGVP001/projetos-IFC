from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Criar uma nova campanha"""
    db_campaign = Campaign(
        name=campaign.name,
        description=campaign.description,
        system=campaign.system,
        max_players=campaign.max_players,
        is_active=campaign.is_active,
        is_public=campaign.is_public,
        setting=campaign.setting,
        rules=campaign.rules,
        notes=campaign.notes,
        master_name=campaign.master_name
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign


@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas as campanhas"""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Obter uma campanha específica"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    """Atualizar uma campanha"""
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    for field, value in campaign.dict(exclude_unset=True).items():
        setattr(db_campaign, field, value)
    
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Deletar uma campanha"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    db.delete(campaign)
    db.commit()
    
    return {"message": "Campanha deletada com sucesso"}
