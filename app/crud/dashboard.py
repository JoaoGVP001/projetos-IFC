from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.models.venda import Venda


def obter_resumo(db: Session, limite_estoque: int) -> dict[str, int | Decimal]:
    inicio_hoje = datetime.combine(datetime.now().date(), time.min)

    return {
        "total_produtos": db.query(func.count(Produto.id)).scalar() or 0,
        "total_vendas": db.query(func.count(Venda.id)).scalar() or 0,
        "faturamento_total": db.query(func.coalesce(func.sum(Venda.valor_total), 0)).scalar(),
        "produtos_estoque_baixo": (
            db.query(func.count(Produto.id))
            .filter(Produto.quantidade_estoque <= limite_estoque)
            .scalar()
            or 0
        ),
        "vendas_hoje": (
            db.query(func.count(Venda.id)).filter(Venda.data >= inicio_hoje).scalar() or 0
        ),
        "faturamento_hoje": (
            db.query(func.coalesce(func.sum(Venda.valor_total), 0))
            .filter(Venda.data >= inicio_hoje)
            .scalar()
        ),
    }
