from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    data = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
    valor_total = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="CONCLUIDA")
    data_cancelamento = Column(DateTime, nullable=True)
    motivo_cancelamento = Column(String(255), nullable=True)

    itens = relationship(
        "ItemVenda", back_populates="venda", cascade="all, delete-orphan"
    )
    cliente = relationship("Cliente", back_populates="vendas")


class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)

    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")

    @property
    def produto_nome(self) -> str:
        return self.produto.nome

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade
