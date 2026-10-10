from sqlalchemy import Column, Integer, String, Numeric

from app.core.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    codigo_barras = Column(String(50), unique=True, nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    quantidade_estoque = Column(Integer, default=0)
