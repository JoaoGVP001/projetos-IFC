from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.venda import VendaCreate, VendaOut
from app.crud import venda as crud_venda
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/vendas",
    tags=["Vendas"],
    dependencies=[Depends(get_current_user)],  # todas as rotas abaixo exigem login
)


@router.post("", response_model=VendaOut, status_code=status.HTTP_201_CREATED)
def registrar_venda(
    venda: VendaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_user),
):
    try:
        return crud_venda.criar_venda(db, usuario_id=usuario_atual.id, venda=venda)
    except crud_venda.EstoqueInsuficienteError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except crud_venda.ProdutoNaoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=list[VendaOut])
def listar(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud_venda.listar_vendas(db, skip, limit)


@router.get("/{venda_id}", response_model=VendaOut)
def obter(venda_id: int, db: Session = Depends(get_db)):
    venda = crud_venda.obter_venda(db, venda_id)
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda
