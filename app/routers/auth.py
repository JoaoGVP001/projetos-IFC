from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token
from app.crud.usuario import criar_usuario, get_usuario_by_username, autenticar_usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if get_usuario_by_username(db, usuario.username):
        raise HTTPException(status_code=400, detail="Username já está em uso")
    return criar_usuario(db, usuario)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login no padrão OAuth2 (username + password via form).
    Testável direto na tela /docs do FastAPI.
    """
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}
