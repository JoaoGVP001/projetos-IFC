from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI: abre uma sessão por requisição
    e garante que ela é fechada no final, mesmo se der erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
