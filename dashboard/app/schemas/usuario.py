from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.usuario import PerfilUsuario


class UsuarioBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=6)  # senha em texto puro, só chega até aqui — vira hash antes de salvar


class UsuarioOut(UsuarioBase):
    id: int
    ativo: bool
    perfil: PerfilUsuario

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
