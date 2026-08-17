from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemVendaCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que zero")


class VendaCreate(BaseModel):
    itens: list[ItemVendaCreate] = Field(min_length=1)


class ItemVendaOut(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal

    model_config = ConfigDict(from_attributes=True)


class VendaOut(BaseModel):
    id: int
    usuario_id: int
    data: datetime
    valor_total: Decimal
    itens: list[ItemVendaOut]

    model_config = ConfigDict(from_attributes=True)
