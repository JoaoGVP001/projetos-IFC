from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, dashboard, produtos, venda

app = FastAPI(
    title="Dashboard de Vendas e Estoque",
    description="API para gestão de produtos, estoque e autenticação de usuários",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(produtos.router)
app.include_router(venda.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Status"])
def status():
    return {"status": "online"}
