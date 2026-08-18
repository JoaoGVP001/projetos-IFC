from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntradaEstoqueCreate(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)
    descricao: str | None = Field(default=None, max_length=255)


class AjusteEstoqueCreate(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(description="Use valor positivo ou negativo")
    descricao: str = Field(min_length=3, max_length=255)

    @field_validator("quantidade")
    @classmethod
    def quantidade_nao_pode_ser_zero(cls, valor: int) -> int:
        if valor == 0:
            raise ValueError("Quantidade do ajuste nao pode ser zero")
        return valor


class SaldoEstoqueOut(BaseModel):
    produto_id: int
    quantidade_disponivel: int
    quantidade_reservada: int


class MovimentacaoEstoqueOut(BaseModel):
    id: int
    produto_id: int
    tipo: str
    quantidade: int
    origem: str
    descricao: str | None
    venda_id: int | None
    usuario_id: int | None
    data: datetime

    model_config = ConfigDict(from_attributes=True)
