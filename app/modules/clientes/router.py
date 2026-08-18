from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.clientes.models import Cliente
from app.modules.clientes.schemas import ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ClienteOut])
def listar(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    busca: str | None = Query(default=None, min_length=1, max_length=150),
    db: Session = Depends(get_db),
):
    consulta = db.query(Cliente)
    if busca:
        consulta = consulta.filter(Cliente.nome.ilike(f"%{busca.strip()}%"))
    return consulta.order_by(Cliente.nome).offset(skip).limit(limit).all()


@router.post("", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def criar(cliente: ClienteCreate, db: Session = Depends(get_db)):
    novo_cliente = Cliente(**cliente.model_dump())
    db.add(novo_cliente)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=409, detail="CPF/CNPJ ja esta cadastrado") from erro
    db.refresh(novo_cliente)
    return novo_cliente


@router.get("/{cliente_id}", response_model=ClienteOut)
def obter(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def atualizar(cliente_id: int, dados: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    try:
        db.commit()
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=409, detail="CPF/CNPJ ja esta cadastrado") from erro
    db.refresh(cliente)
    return cliente
