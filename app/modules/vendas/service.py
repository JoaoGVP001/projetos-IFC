from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, selectinload

from app.models.venda import ItemVenda, Venda
from app.modules.clientes.models import Cliente
from app.modules.estoque.service import EstoqueService
from app.schemas.venda import VendaCreate


class ClienteNaoEncontradoError(Exception):
    def __init__(self, cliente_id: int):
        super().__init__(f"Cliente {cliente_id} nao encontrado")


class VendaNaoEncontradaError(Exception):
    def __init__(self, venda_id: int):
        super().__init__(f"Venda {venda_id} nao encontrada")


class VendaNaoCancelavelError(Exception):
    def __init__(self, venda_id: int):
        super().__init__(f"Venda {venda_id} ja esta cancelada")


class VendaService:
    def __init__(self, db: Session):
        self.db = db
        self.estoque = EstoqueService(db)

    def listar(self, skip: int = 0, limit: int = 100) -> list[Venda]:
        return (
            self.db.query(Venda)
            .options(selectinload(Venda.itens).selectinload(ItemVenda.produto))
            .order_by(Venda.data.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obter(self, venda_id: int) -> Venda | None:
        return (
            self.db.query(Venda)
            .options(selectinload(Venda.itens).selectinload(ItemVenda.produto))
            .filter(Venda.id == venda_id)
            .first()
        )

    def criar(self, usuario_id: int, dados: VendaCreate) -> Venda:
        if dados.cliente_id and not self.db.query(Cliente.id).filter(Cliente.id == dados.cliente_id).first():
            raise ClienteNaoEncontradoError(dados.cliente_id)

        quantidades: dict[int, int] = {}
        for item in dados.itens:
            quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade

        try:
            venda = Venda(usuario_id=usuario_id, cliente_id=dados.cliente_id, valor_total=Decimal("0"))
            self.db.add(venda)
            self.db.flush()

            valor_total = Decimal("0")
            for produto_id, quantidade in quantidades.items():
                reserva = self.estoque.reservar(produto_id, quantidade, usuario_id)
                produto = self.estoque._produto_bloqueado(produto_id)
                venda.itens.append(
                    ItemVenda(
                        produto_id=produto_id,
                        quantidade=quantidade,
                        preco_unitario=produto.preco,
                    )
                )
                valor_total += produto.preco * quantidade
                self.estoque.confirmar_baixa(reserva, venda.id)

            venda.valor_total = valor_total
            self.db.commit()
            return self.obter(venda.id)  # Recarrega os relacionamentos do contrato da API.
        except Exception:
            self.db.rollback()
            raise

    def cancelar(self, venda_id: int, usuario_id: int, motivo: str) -> Venda:
        venda = self.obter(venda_id)
        if not venda:
            raise VendaNaoEncontradaError(venda_id)
        if venda.status != "CONCLUIDA":
            raise VendaNaoCancelavelError(venda_id)

        try:
            for item in venda.itens:
                self.estoque.devolver_por_cancelamento(
                    item.produto_id, item.quantidade, venda.id, usuario_id
                )
            venda.status = "CANCELADA"
            venda.data_cancelamento = datetime.now(timezone.utc).replace(tzinfo=None)
            venda.motivo_cancelamento = motivo
            self.db.commit()
            return self.obter(venda.id)
        except Exception:
            self.db.rollback()
            raise
