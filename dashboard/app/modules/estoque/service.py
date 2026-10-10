from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.modules.estoque.models import MovimentacaoEstoque, ReservaEstoque


class EstoqueInsuficienteError(Exception):
    def __init__(self, produto_nome: str, disponivel: int, solicitado: int):
        super().__init__(
            f"Estoque insuficiente para '{produto_nome}': "
            f"disponivel {disponivel}, solicitado {solicitado}"
        )


class ProdutoNaoEncontradoError(Exception):
    def __init__(self, produto_id: int):
        super().__init__(f"Produto {produto_id} nao encontrado")


class EstoqueService:
    """Centraliza alteracoes no saldo e seu historico auditavel."""

    def __init__(self, db: Session):
        self.db = db

    def _produto_bloqueado(self, produto_id: int) -> Produto:
        produto = (
            self.db.query(Produto)
            .filter(Produto.id == produto_id)
            .with_for_update()
            .first()
        )
        if not produto:
            raise ProdutoNaoEncontradoError(produto_id)
        return produto

    def _reservado(self, produto_id: int) -> int:
        return (
            self.db.query(func.coalesce(func.sum(ReservaEstoque.quantidade), 0))
            .filter(
                ReservaEstoque.produto_id == produto_id,
                ReservaEstoque.status == "ATIVA",
            )
            .scalar()
            or 0
        )

    def saldo(self, produto_id: int) -> tuple[int, int]:
        produto = self._produto_bloqueado(produto_id)
        reservado = self._reservado(produto_id)
        return produto.quantidade_estoque - reservado, reservado

    def _movimentar(
        self,
        *,
        produto_id: int,
        tipo: str,
        quantidade: int,
        origem: str,
        usuario_id: int | None = None,
        venda_id: int | None = None,
        descricao: str | None = None,
    ) -> None:
        self.db.add(
            MovimentacaoEstoque(
                produto_id=produto_id,
                tipo=tipo,
                quantidade=quantidade,
                origem=origem,
                usuario_id=usuario_id,
                venda_id=venda_id,
                descricao=descricao,
            )
        )

    def registrar_entrada(
        self, produto_id: int, quantidade: int, usuario_id: int, descricao: str | None = None
    ) -> Produto:
        produto = self._produto_bloqueado(produto_id)
        produto.quantidade_estoque += quantidade
        self._movimentar(
            produto_id=produto_id,
            tipo="ENTRADA",
            quantidade=quantidade,
            origem="ENTRADA_MANUAL",
            usuario_id=usuario_id,
            descricao=descricao,
        )
        return produto

    def ajustar(
        self, produto_id: int, quantidade: int, usuario_id: int, descricao: str
    ) -> Produto:
        produto = self._produto_bloqueado(produto_id)
        novo_saldo = produto.quantidade_estoque + quantidade
        if novo_saldo < 0:
            raise EstoqueInsuficienteError(produto.nome, produto.quantidade_estoque, -quantidade)
        produto.quantidade_estoque = novo_saldo
        self._movimentar(
            produto_id=produto_id,
            tipo="AJUSTE",
            quantidade=quantidade,
            origem="AJUSTE_MANUAL",
            usuario_id=usuario_id,
            descricao=descricao,
        )
        return produto

    def reservar(self, produto_id: int, quantidade: int, usuario_id: int) -> ReservaEstoque:
        produto = self._produto_bloqueado(produto_id)
        disponivel = produto.quantidade_estoque - self._reservado(produto_id)
        if disponivel < quantidade:
            raise EstoqueInsuficienteError(produto.nome, disponivel, quantidade)
        reserva = ReservaEstoque(
            produto_id=produto_id,
            quantidade=quantidade,
            origem="VENDA",
            usuario_id=usuario_id,
        )
        self.db.add(reserva)
        self.db.flush()
        self._movimentar(
            produto_id=produto_id,
            tipo="RESERVA",
            quantidade=quantidade,
            origem="VENDA",
            usuario_id=usuario_id,
        )
        return reserva

    def confirmar_baixa(self, reserva: ReservaEstoque, venda_id: int) -> None:
        produto = self._produto_bloqueado(reserva.produto_id)
        produto.quantidade_estoque -= reserva.quantidade
        reserva.status = "CONFIRMADA"
        reserva.venda_id = venda_id
        self._movimentar(
            produto_id=produto.id,
            tipo="SAIDA",
            quantidade=reserva.quantidade,
            origem="VENDA",
            usuario_id=reserva.usuario_id,
            venda_id=venda_id,
        )

    def liberar_reserva(self, reserva: ReservaEstoque) -> None:
        if reserva.status != "ATIVA":
            return
        reserva.status = "CANCELADA"
        self._movimentar(
            produto_id=reserva.produto_id,
            tipo="LIBERACAO_RESERVA",
            quantidade=reserva.quantidade,
            origem=reserva.origem,
            usuario_id=reserva.usuario_id,
        )

    def devolver_por_cancelamento(
        self, produto_id: int, quantidade: int, venda_id: int, usuario_id: int
    ) -> None:
        produto = self._produto_bloqueado(produto_id)
        produto.quantidade_estoque += quantidade
        self._movimentar(
            produto_id=produto_id,
            tipo="DEVOLUCAO",
            quantidade=quantidade,
            origem="CANCELAMENTO_VENDA",
            usuario_id=usuario_id,
            venda_id=venda_id,
        )
