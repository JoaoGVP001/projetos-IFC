from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=False)  # Classe do personagem
    race = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # Atributos básicos
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # HP e outros stats
    hit_points = Column(Integer, default=10)
    max_hit_points = Column(Integer, default=10)
    armor_class = Column(Integer, default=10)
    speed = Column(Integer, default=30)
    
    # Informações adicionais
    background = Column(Text)
    alignment = Column(String(20))
    backstory = Column(Text)
    appearance = Column(Text)
    personality = Column(Text)
    
    # Dados em JSON para habilidades, magias, etc.
    abilities = Column(JSON, default=dict)
    spells = Column(JSON, default=dict)
    equipment = Column(JSON, default=dict)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="characters")
    campaign = relationship("Campaign", back_populates="characters")
    items = relationship("Item", secondary="character_items", back_populates="characters")
