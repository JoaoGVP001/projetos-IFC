from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.crud.dashboard import obter_resumo
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.dashboard import DashboardResumo

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/resumo", response_model=DashboardResumo)
def resumo(
    limite_estoque: int = Query(default=5, ge=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles(PerfilUsuario.ADMIN)),
):
    return obter_resumo(db, limite_estoque)
