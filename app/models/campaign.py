from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

# Tabela de associação para jogadores em campanhas
campaign_players = Table(
    'campaign_players',
    Base.metadata,
    Column('campaign_id', Integer, ForeignKey('campaigns.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    system = Column(String(50), default="D&D 5e")  # Sistema de RPG
    max_players = Column(Integer, default=6)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Configurações da campanha
    setting = Column(Text)  # Cenário/mundo da campanha
    rules = Column(Text)    # Regras específicas
    notes = Column(Text)    # Notas do mestre
    
    # Foreign Keys
    master_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    master = relationship("User", back_populates="campaigns_as_master", foreign_keys=[master_id])
    players = relationship("User", back_populates="campaigns_as_player", secondary=campaign_players)
    characters = relationship("Character", back_populates="campaign")
