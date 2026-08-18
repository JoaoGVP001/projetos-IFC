from sqlalchemy.orm import Session, selectinload

from app.models.produto import Produto
from app.models.venda import Venda, ItemVenda
from app.schemas.venda import VendaCreate


class EstoqueInsuficienteError(Exception):
    """Lançado quando um produto não tem estoque suficiente para a venda."""

    def __init__(self, produto_nome: str, disponivel: int, solicitado: int):
        self.produto_nome = produto_nome
        self.disponivel = disponivel
        self.solicitado = solicitado
        super().__init__(
            f"Estoque insuficiente para '{produto_nome}': "
            f"disponível {disponivel}, solicitado {solicitado}"
        )


class ProdutoNaoEncontradoError(Exception):
    """Lançado quando um produto_id informado na venda não existe."""

    def __init__(self, produto_id: int):
        self.produto_id = produto_id
        super().__init__(f"Produto {produto_id} não encontrado")


def listar_vendas(db: Session, skip: int = 0, limit: int = 100) -> list[Venda]:
    return (
        db.query(Venda)
        .options(selectinload(Venda.itens).selectinload(ItemVenda.produto))
        .order_by(Venda.data.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return (
        db.query(Venda)
        .options(selectinload(Venda.itens).selectinload(ItemVenda.produto))
        .filter(Venda.id == venda_id)
        .first()
    )


def criar_venda(db: Session, usuario_id: int, venda: VendaCreate) -> Venda:
    """
    Cria uma venda com seus itens, validando estoque e descontando
    a quantidade vendida de cada produto. Tudo dentro de uma única
    transação: se qualquer item falhar, nada é gravado.
    """
    quantidades_por_produto: dict[int, int] = {}

    for item in venda.itens:
        quantidades_por_produto[item.produto_id] = (
            quantidades_por_produto.get(item.produto_id, 0) + item.quantidade
        )

    produtos_cache: dict[int, Produto] = {}

    # 1. Validar todos os itens antes de mexer em qualquer coisa
    for produto_id, quantidade in quantidades_por_produto.items():
        produto = (
            db.query(Produto)
            .filter(Produto.id == produto_id)
            .with_for_update()
            .first()
        )
        if not produto:
            raise ProdutoNaoEncontradoError(produto_id)
        if produto.quantidade_estoque < quantidade:
            raise EstoqueInsuficienteError(
                produto.nome, produto.quantidade_estoque, quantidade
            )
        produtos_cache[produto_id] = produto

    # 2. Calcular o valor total e montar os itens da venda
    valor_total = sum(
        produtos_cache[produto_id].preco * quantidade
        for produto_id, quantidade in quantidades_por_produto.items()
    )

    nova_venda = Venda(usuario_id=usuario_id, valor_total=valor_total)

    for produto_id, quantidade in quantidades_por_produto.items():
        produto = produtos_cache[produto_id]
        nova_venda.itens.append(
            ItemVenda(
                produto_id=produto.id,
                quantidade=quantidade,
                preco_unitario=produto.preco,
            )
        )
        # 3. Baixa de estoque
        produto.quantidade_estoque -= quantidade

    try:
        db.add(nova_venda)
        db.commit()
        db.refresh(nova_venda)
    except Exception:
        db.rollback()
        raise

    return nova_venda
