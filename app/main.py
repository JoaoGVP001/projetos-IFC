from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, produtos

# Cria as tabelas no banco automaticamente se ainda não existirem.
# Para projetos maiores, o ideal é trocar isso por migrations com Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dashboard de Vendas e Estoque",
    description="API para gestão de produtos, estoque e autenticação de usuários",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(produtos.router)


@app.get("/", tags=["Status"])
def status():
    return {"status": "online"}
