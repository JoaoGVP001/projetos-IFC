from pydantic import BaseModel, EmailStr, ConfigDict


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str  # senha em texto puro, só chega até aqui — vira hash antes de salvar


class UsuarioOut(UsuarioBase):
    id: int
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
