from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que zero")


class VendaCreate(BaseModel):
    itens: list[ItemVendaCreate] = Field(min_length=1)
    cliente_id: int | None = Field(default=None, gt=0)


class VendaCancelamento(BaseModel):
    motivo: str = Field(min_length=3, max_length=255)


class ItemVendaOut(BaseModel):
    id: int
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class VendaOut(BaseModel):
    id: int
    usuario_id: int
    cliente_id: int | None
    data: datetime
    valor_total: Decimal
    status: str
    data_cancelamento: datetime | None
    motivo_cancelamento: str | None
    itens: list[ItemVendaOut]

    model_config = ConfigDict(from_attributes=True)
