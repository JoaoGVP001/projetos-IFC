from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.usuario import PerfilUsuario, Usuario
from app.modules.estoque.models import MovimentacaoEstoque
from app.modules.estoque.schemas import (
    AjusteEstoqueCreate,
    EntradaEstoqueCreate,
    MovimentacaoEstoqueOut,
    SaldoEstoqueOut,
)
from app.modules.estoque.service import EstoqueInsuficienteError, EstoqueService, ProdutoNaoEncontradoError
from app.schemas.produto import ProdutoOut

router = APIRouter(
    prefix="/estoque",
    tags=["Estoque"],
    dependencies=[Depends(get_current_user)],
)


def _erro_estoque(erro: Exception) -> HTTPException:
    if isinstance(erro, ProdutoNaoEncontradoError):
        return HTTPException(status_code=404, detail=str(erro))
    return HTTPException(status_code=400, detail=str(erro))


@router.get("/movimentacoes", response_model=list[MovimentacaoEstoqueOut])
def listar_movimentacoes(
    produto_id: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = db.query(MovimentacaoEstoque)
    if produto_id:
        consulta = consulta.filter(MovimentacaoEstoque.produto_id == produto_id)
    return consulta.order_by(MovimentacaoEstoque.data.desc()).offset(skip).limit(limit).all()


@router.get("/{produto_id}", response_model=SaldoEstoqueOut)
def consultar_saldo(produto_id: int, db: Session = Depends(get_db)):
    try:
        disponivel, reservado = EstoqueService(db).saldo(produto_id)
    except ProdutoNaoEncontradoError as erro:
        raise _erro_estoque(erro)
    return SaldoEstoqueOut(
        produto_id=produto_id,
        quantidade_disponivel=disponivel,
        quantidade_reservada=reservado,
    )


@router.post("/entradas", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def registrar_entrada(
    dados: EntradaEstoqueCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    try:
        produto = EstoqueService(db).registrar_entrada(
            dados.produto_id, dados.quantidade, usuario.id, dados.descricao
        )
        db.commit()
        db.refresh(produto)
        return produto
    except (ProdutoNaoEncontradoError, EstoqueInsuficienteError) as erro:
        db.rollback()
        raise _erro_estoque(erro)


@router.post("/ajustes", response_model=ProdutoOut)
def ajustar_estoque(
    dados: AjusteEstoqueCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    try:
        produto = EstoqueService(db).ajustar(
            dados.produto_id, dados.quantidade, usuario.id, dados.descricao
        )
        db.commit()
        db.refresh(produto)
        return produto
    except (ProdutoNaoEncontradoError, EstoqueInsuficienteError) as erro:
        db.rollback()
        raise _erro_estoque(erro)
