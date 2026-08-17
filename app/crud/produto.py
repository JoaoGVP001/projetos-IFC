from sqlalchemy.orm import Session

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate


def listar_produtos(db: Session, skip: int = 0, limit: int = 100) -> list[Produto]:
    return db.query(Produto).offset(skip).limit(limit).all()


def obter_produto(db: Session, produto_id: int) -> Produto | None:
    return db.query(Produto).filter(Produto.id == produto_id).first()


def criar_produto(db: Session, produto: ProdutoCreate) -> Produto:
    novo_produto = Produto(**produto.model_dump())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


def atualizar_produto(db: Session, produto_id: int, dados: ProdutoUpdate) -> Produto | None:
    produto = obter_produto(db, produto_id)
    if not produto:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto_id: int) -> bool:
    produto = obter_produto(db, produto_id)
    if not produto:
        return False
    db.delete(produto)
    db.commit()
    return True
