from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.campaign import Campaign
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate


class CampaignService:
    @staticmethod
    def create_campaign(db: Session, campaign: CampaignCreate, master_id: int) -> Campaign:
        """Create a new campaign"""
        db_campaign = Campaign(
            **campaign.dict(),
            master_id=master_id
        )
        
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def get_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    @staticmethod
    def get_campaigns_by_master(db: Session, master_id: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get campaigns by master ID"""
        return db.query(Campaign).filter(Campaign.master_id == master_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_public_campaigns(db: Session, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get public campaigns"""
        return db.query(Campaign).filter(
            and_(Campaign.is_public == True, Campaign.is_active == True)
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_campaigns(db: Session, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get all campaigns with pagination"""
        return db.query(Campaign).offset(skip).limit(limit).all()

    @staticmethod
    def update_campaign(db: Session, campaign_id: int, campaign_update: CampaignUpdate) -> Optional[Campaign]:
        """Update campaign"""
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return None
        
        update_data = campaign_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_campaign, field, value)
        
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: int) -> bool:
        """Delete campaign"""
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return False
        
        db.delete(db_campaign)
        db.commit()
        return True

    @staticmethod
    def add_player_to_campaign(db: Session, campaign_id: int, user_id: int) -> Optional[Campaign]:
        """Add player to campaign"""
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_campaign or not db_user:
            return None
        
        # Check if player is already in campaign
        if db_user in db_campaign.players:
            return db_campaign
        
        # Check if campaign is full
        if len(db_campaign.players) >= db_campaign.max_players:
            return None
        
        db_campaign.players.append(db_user)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def remove_player_from_campaign(db: Session, campaign_id: int, user_id: int) -> Optional[Campaign]:
        """Remove player from campaign"""
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_campaign or not db_user:
            return None
        
        if db_user in db_campaign.players:
            db_campaign.players.remove(db_user)
            db.commit()
            db.refresh(db_campaign)
        
        return db_campaign

    @staticmethod
    def get_campaign_stats(db: Session, campaign_id: int) -> dict:
        """Get campaign statistics"""
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return {}
        
        return {
            "players_count": len(db_campaign.players),
            "characters_count": len(db_campaign.characters),
            "max_players": db_campaign.max_players
        }
