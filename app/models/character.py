from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    name = Column(String(100), nullable=False)
    player_name = Column(String(100), nullable=False)
    origin = Column(String(50), nullable=False)
    character_class = Column(String(50), nullable=False)
    nex = Column(Integer, default=5)  # NEX entre 5 e 99
    avatar_url = Column(String(255))

    # Atributos do sistema Sigil
    agilidade = Column(Integer, default=1)  # Valor entre 0 e 3
    intelecto = Column(Integer, default=1)  # Valor entre 0 e 3
    vigor = Column(Integer, default=1)      # Valor entre 0 e 3
    presenca = Column(Integer, default=1)   # Valor entre 0 e 3
    forca = Column(Integer, default=1)      # Valor entre 0 e 3

    # Detalhes opcionais
    gender = Column(String(20))
    age = Column(Integer)
    appearance = Column(Text)
    personality = Column(Text)
    background = Column(Text)
    objective = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    campaign = relationship("Campaign", back_populates="characters")
