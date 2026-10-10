from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    cpf_cnpj = Column(String(14), unique=True, nullable=True, index=True)
    email = Column(String(120), nullable=True)
    telefone = Column(String(30), nullable=True)
    endereco = Column(String(255), nullable=True)

    vendas = relationship("Venda", back_populates="cliente")
