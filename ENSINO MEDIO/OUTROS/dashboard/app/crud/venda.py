from sqlalchemy.orm import Session

from app.models.venda import Venda
from app.modules.estoque.service import EstoqueInsuficienteError, ProdutoNaoEncontradoError
from app.modules.vendas.service import VendaService
from app.schemas.venda import VendaCreate


def listar_vendas(db: Session, skip: int = 0, limit: int = 100) -> list[Venda]:
    return VendaService(db).listar(skip, limit)


def obter_venda(db: Session, venda_id: int) -> Venda | None:
    return VendaService(db).obter(venda_id)


def criar_venda(db: Session, usuario_id: int, venda: VendaCreate) -> Venda:
    return VendaService(db).criar(usuario_id, venda)
