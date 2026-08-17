from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import hash_password, verify_password


def get_usuario_by_username(db: Session, username: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.username == username).first()


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    novo_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        senha_hash=hash_password(usuario.senha),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def autenticar_usuario(db: Session, username: str, senha: str) -> Usuario | None:
    usuario = get_usuario_by_username(db, username)
    if not usuario:
        return None
    if not verify_password(senha, usuario.senha_hash):
        return None
    return usuario
