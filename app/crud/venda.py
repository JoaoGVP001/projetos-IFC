from sqlalchemy.orm import Session

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
    return db.query(Venda).offset(skip).limit(limit).all()


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return db.query(Venda).filter(Venda.id == venda_id).first()


def criar_venda(db: Session, usuario_id: int, venda: VendaCreate) -> Venda:
    """
    Cria uma venda com seus itens, validando estoque e descontando
    a quantidade vendida de cada produto. Tudo dentro de uma única
    transação: se qualquer item falhar, nada é gravado.
    """
    produtos_cache: dict[int, Produto] = {}

    # 1. Validar todos os itens antes de mexer em qualquer coisa
    for item in venda.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise ProdutoNaoEncontradoError(item.produto_id)
        if produto.quantidade_estoque < item.quantidade:
            raise EstoqueInsuficienteError(
                produto.nome, produto.quantidade_estoque, item.quantidade
            )
        produtos_cache[item.produto_id] = produto

    # 2. Calcular o valor total e montar os itens da venda
    valor_total = sum(
        produtos_cache[item.produto_id].preco * item.quantidade
        for item in venda.itens
    )

    nova_venda = Venda(usuario_id=usuario_id, valor_total=valor_total)

    for item in venda.itens:
        produto = produtos_cache[item.produto_id]
        nova_venda.itens.append(
            ItemVenda(
                produto_id=produto.id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )
        # 3. Baixa de estoque
        produto.quantidade_estoque -= item.quantidade

    try:
        db.add(nova_venda)
        db.commit()
        db.refresh(nova_venda)
    except Exception:
        db.rollback()
        raise

    return nova_venda
