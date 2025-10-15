from typing import List
from fastapi import APIRouter
from app.schemas.campaigns import CampaignCreate, CampaignOut

router = APIRouter()

_campaigns: List[CampaignOut] = []

@router.get("/", response_model=List[CampaignOut])
async def list_campaigns():
    return _campaigns

@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign(payload: CampaignCreate):
    new = CampaignOut(
        id=str(len(_campaigns) + 1),
        name=payload.name,
        description=payload.description or "",
        masterId=payload.masterId or "",
    )
    _campaigns.append(new)
    return new

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.auth_service import AuthService
from app.services.campaign_service import CampaignService
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignWithDetails, CampaignJoin
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    return CampaignService.create_campaign(db=db, campaign=campaign, master_id=current_user.id)


@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    public_only: bool = False,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get campaigns"""
    if public_only:
        return CampaignService.get_public_campaigns(db=db, skip=skip, limit=limit)
    else:
        return CampaignService.get_all_campaigns(db=db, skip=skip, limit=limit)


@router.get("/public", response_model=List[CampaignResponse])
async def get_public_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get public campaigns (no authentication required)"""
    return CampaignService.get_public_campaigns(db=db, skip=skip, limit=limit)


@router.get("/my", response_model=List[CampaignResponse])
async def get_my_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's campaigns (as master)"""
    return CampaignService.get_campaigns_by_master(db=db, master_id=current_user.id, skip=skip, limit=limit)


@router.get("/{campaign_id}", response_model=CampaignWithDetails)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get campaign by ID with details"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get campaign stats
    stats = CampaignService.get_campaign_stats(db=db, campaign_id=campaign_id)
    
    campaign_details = CampaignWithDetails(
        **campaign.__dict__,
        **stats
    )
    
    return campaign_details


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update campaign"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Only the master can update the campaign unless user is admin
    if campaign.master_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return CampaignService.update_campaign(db=db, campaign_id=campaign_id, campaign_update=campaign_update)


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete campaign"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Only the master can delete the campaign unless user is admin
    if campaign.master_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = CampaignService.delete_campaign(db=db, campaign_id=campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {"message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/join")
async def join_campaign(
    campaign_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a campaign"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if campaign is public or user is already a player
    if not campaign.is_public and current_user not in campaign.players:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign is not public or you don't have permission to join"
        )
    
    updated_campaign = CampaignService.add_player_to_campaign(db=db, campaign_id=campaign_id, user_id=current_user.id)
    if updated_campaign is None:
        raise HTTPException(status_code=400, detail="Failed to join campaign")
    
    return {"message": "Successfully joined campaign"}


@router.delete("/{campaign_id}/leave")
async def leave_campaign(
    campaign_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a campaign"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    updated_campaign = CampaignService.remove_player_from_campaign(db=db, campaign_id=campaign_id, user_id=current_user.id)
    if updated_campaign is None:
        raise HTTPException(status_code=400, detail="Failed to leave campaign")
    
    return {"message": "Successfully left campaign"}


@router.post("/{campaign_id}/players/{user_id}")
async def add_player_to_campaign(
    campaign_id: int,
    user_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add player to campaign (master only)"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Only the master can add players unless user is admin
    if campaign.master_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_campaign = CampaignService.add_player_to_campaign(db=db, campaign_id=campaign_id, user_id=user_id)
    if updated_campaign is None:
        raise HTTPException(status_code=400, detail="Failed to add player to campaign")
    
    return {"message": "Player added to campaign successfully"}


@router.delete("/{campaign_id}/players/{user_id}")
async def remove_player_from_campaign(
    campaign_id: int,
    user_id: int,
    current_user: User = Depends(AuthService.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove player from campaign (master only)"""
    campaign = CampaignService.get_campaign(db=db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Only the master can remove players unless user is admin
    if campaign.master_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_campaign = CampaignService.remove_player_from_campaign(db=db, campaign_id=campaign_id, user_id=user_id)
    if updated_campaign is None:
        raise HTTPException(status_code=400, detail="Failed to remove player from campaign")
    
    return {"message": "Player removed from campaign successfully"}
