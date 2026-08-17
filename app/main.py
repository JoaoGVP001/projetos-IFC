from fastapi import FastAPI

from app.routers import auth, produtos

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
