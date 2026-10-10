from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.modules.estoque.models import MovimentacaoEstoque, ReservaEstoque
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


class ProdutoConflitoError(Exception):
    pass


class ProdutoComVendasError(Exception):
    pass


def listar_produtos(
    db: Session, skip: int = 0, limit: int = 100, busca: str | None = None
) -> list[Produto]:
    query = db.query(Produto)
    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca.strip()}%"))
    return query.order_by(Produto.nome).offset(skip).limit(limit).all()


def listar_estoque_baixo(db: Session, limite: int) -> list[Produto]:
    return (
        db.query(Produto)
        .filter(Produto.quantidade_estoque <= limite)
        .order_by(Produto.quantidade_estoque, Produto.nome)
        .all()
    )


def obter_produto(db: Session, produto_id: int) -> Produto | None:
    return db.query(Produto).filter(Produto.id == produto_id).first()


def criar_produto(db: Session, produto: ProdutoCreate, commit: bool = True) -> Produto:
    novo_produto = Produto(**produto.model_dump())
    db.add(novo_produto)
    try:
        if commit:
            db.commit()
        else:
            db.flush()
    except IntegrityError as error:
        db.rollback()
        raise ProdutoConflitoError(
            "Já existe um produto com este código de barras"
        ) from error
    if commit:
        db.refresh(novo_produto)
    return novo_produto


def atualizar_produto(
    db: Session, produto_id: int, dados: ProdutoUpdate, commit: bool = True
) -> Produto | None:
    produto = obter_produto(db, produto_id)
    if not produto:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    try:
        if commit:
            db.commit()
        else:
            db.flush()
    except IntegrityError as error:
        db.rollback()
        raise ProdutoConflitoError(
            "Já existe um produto com este código de barras"
        ) from error
    if commit:
        db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto_id: int) -> bool:
    produto = obter_produto(db, produto_id)
    if not produto:
        return False
    # Produtos sem vendas podem ser removidos junto das movimentacoes de cadastro.
    db.query(ReservaEstoque).filter(ReservaEstoque.produto_id == produto_id).delete()
    db.query(MovimentacaoEstoque).filter(
        MovimentacaoEstoque.produto_id == produto_id,
        MovimentacaoEstoque.venda_id.is_(None),
    ).delete()
    db.delete(produto)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ProdutoComVendasError(
            "Não é possível excluir um produto que possui vendas"
        ) from error
    return True
