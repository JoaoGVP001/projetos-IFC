from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoOut
from app.crud import produto as crud_produto

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    dependencies=[Depends(get_current_user)],  # todas as rotas abaixo exigem login
)


@router.get("/", response_model=list[ProdutoOut])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_produto.listar_produtos(db, skip, limit)


@router.get("/{produto_id}", response_model=ProdutoOut)
def obter(produto_id: int, db: Session = Depends(get_db)):
    produto = crud_produto.obter_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post("/", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar(produto: ProdutoCreate, db: Session = Depends(get_db)):
    return crud_produto.criar_produto(db, produto)


@router.put("/{produto_id}", response_model=ProdutoOut)
def atualizar(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = crud_produto.atualizar_produto(db, produto_id, dados)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(produto_id: int, db: Session = Depends(get_db)):
    if not crud_produto.deletar_produto(db, produto_id):
        raise HTTPException(status_code=404, detail="Produto não encontrado")
