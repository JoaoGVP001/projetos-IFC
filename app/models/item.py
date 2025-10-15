from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False)  # weapon, armor, consumable, tool, etc.
    rarity = Column(String(20), default="common")  # common, uncommon, rare, epic, legendary
    
    # Estatísticas do item
    weight = Column(Float, default=0.0)
    value = Column(Integer, default=0)  # Valor em moedas de ouro
    quantity = Column(Integer, default=1)
    
    # Propriedades específicas
    is_magical = Column(Boolean, default=False)
    is_consumable = Column(Boolean, default=False)
    is_equippable = Column(Boolean, default=True)
    
    # Dados em JSON para propriedades específicas
    properties = Column(JSON, default=dict)  # Dano, AC, bônus, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    characters = relationship("Character", secondary="character_items", back_populates="items")
