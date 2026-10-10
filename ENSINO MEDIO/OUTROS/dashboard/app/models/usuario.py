from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String

from app.core.database import Base


class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"
    FISCAL = "FISCAL"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    perfil = Column(String(20), nullable=False, default=PerfilUsuario.OPERADOR.value)
