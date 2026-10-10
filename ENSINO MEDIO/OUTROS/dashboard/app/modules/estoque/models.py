from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    tipo = Column(String(30), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)
    origem = Column(String(50), nullable=False)
    descricao = Column(String(255), nullable=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)


class ReservaEstoque(Base):
    __tablename__ = "reservas_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="ATIVA", index=True)
    origem = Column(String(50), nullable=False)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
