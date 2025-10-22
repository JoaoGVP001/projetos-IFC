from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    system = Column(String(50), default="Sigil RPG")  # Sistema de RPG
    max_players = Column(Integer, default=6)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    # Configurações da campanha
    setting = Column(Text)  # Cenário/mundo da campanha
    rules = Column(Text)    # Regras específicas
    notes = Column(Text)    # Notas do mestre
    master_name = Column(String(100), nullable=False)  # Nome do mestre

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    characters = relationship("Character", back_populates="campaign")
