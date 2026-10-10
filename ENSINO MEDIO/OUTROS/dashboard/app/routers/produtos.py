from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.usuario import PerfilUsuario, Usuario
from app.modules.estoque.service import EstoqueInsuficienteError, EstoqueService
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoOut
from app.crud import produto as crud_produto

router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
    dependencies=[Depends(get_current_user)],  # todas as rotas abaixo exigem login
)


@router.get("", response_model=list[ProdutoOut])
def listar(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    busca: str | None = Query(default=None, min_length=1, max_length=150),
    db: Session = Depends(get_db),
):
    return crud_produto.listar_produtos(db, skip, limit, busca)


@router.get("/estoque-baixo", response_model=list[ProdutoOut])
def estoque_baixo(
    limite: int = Query(default=5, ge=0), db: Session = Depends(get_db)
):
    return crud_produto.listar_estoque_baixo(db, limite)


@router.get("/{produto_id}", response_model=ProdutoOut)
def obter(produto_id: int, db: Session = Depends(get_db)):
    produto = crud_produto.obter_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post("", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    try:
        quantidade_inicial = produto.quantidade_estoque
        produto_sem_saldo = produto.model_copy(update={"quantidade_estoque": 0})
        novo_produto = crud_produto.criar_produto(db, produto_sem_saldo, commit=False)
        if quantidade_inicial:
            EstoqueService(db).registrar_entrada(
                novo_produto.id,
                quantidade_inicial,
                usuario.id,
                "Estoque inicial do cadastro do produto",
            )
        db.commit()
        db.refresh(novo_produto)
        return novo_produto
    except (crud_produto.ProdutoConflitoError, EstoqueInsuficienteError) as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error))


@router.put("/{produto_id}", response_model=ProdutoOut)
def atualizar(
    produto_id: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    try:
        produto_atual = crud_produto.obter_produto(db, produto_id)
        if not produto_atual:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        campos = dados.model_dump(exclude_unset=True)
        estoque_informado = campos.pop("quantidade_estoque", None)
        produto = crud_produto.atualizar_produto(
            db, produto_id, ProdutoUpdate(**campos), commit=False
        )
        if (
            estoque_informado is not None
            and estoque_informado != produto_atual.quantidade_estoque
        ):
            EstoqueService(db).ajustar(
                produto_id,
                estoque_informado - produto_atual.quantidade_estoque,
                usuario.id,
                "Ajuste pelo cadastro do produto",
            )
        db.commit()
        db.refresh(produto)
    except (crud_produto.ProdutoConflitoError, EstoqueInsuficienteError) as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(error))
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    produto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    try:
        deletado = crud_produto.deletar_produto(db, produto_id)
    except crud_produto.ProdutoComVendasError as error:
        raise HTTPException(status_code=409, detail=str(error))
    if not deletado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
