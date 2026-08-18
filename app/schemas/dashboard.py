from decimal import Decimal

from pydantic import BaseModel


class DashboardResumo(BaseModel):
    total_produtos: int
    total_vendas: int
    faturamento_total: Decimal
    produtos_estoque_baixo: int
    vendas_hoje: int
    faturamento_hoje: Decimal
