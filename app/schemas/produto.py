from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    codigo_barras: str | None = None
    preco: Decimal = Field(gt=0, description="Preço deve ser maior que zero")
    quantidade_estoque: int = Field(default=0, ge=0)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: str | None = None
    codigo_barras: str | None = None
    preco: Decimal | None = Field(default=None, gt=0)
    quantidade_estoque: int | None = Field(default=None, ge=0)


class ProdutoOut(ProdutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
