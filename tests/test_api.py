from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


def criar_cliente(db) -> TestClient:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def criar_usuario_e_token(client: TestClient) -> dict[str, str]:
    resposta = client.post(
        "/auth/registrar",
        json={
            "username": "joao",
            "email": "joao@example.com",
            "senha": "senha-segura",
        },
    )
    assert resposta.status_code == 201

    resposta = client.post(
        "/auth/login", data={"username": "joao", "password": "senha-segura"}
    )
    assert resposta.status_code == 200
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_fluxo_frontend_de_autenticacao_produtos_vendas_e_dashboard(db):
    client = criar_cliente(db)
    try:
        assert client.get("/produtos").status_code == 401
        assert client.get(
            "/produtos", headers={"Authorization": "Bearer token-invalido"}
        ).status_code == 401

        headers = criar_usuario_e_token(client)

        resposta = client.get("/auth/me", headers=headers)
        assert resposta.status_code == 200
        assert resposta.json()["username"] == "joao"
        assert "senha_hash" not in resposta.json()

        resposta = client.post(
            "/produtos",
            headers=headers,
            json={"nome": "Caderno", "preco": "19.90", "quantidade_estoque": 5},
        )
        assert resposta.status_code == 201
        produto = resposta.json()

        resposta = client.get("/produtos?busca=cader", headers=headers)
        assert resposta.status_code == 200
        assert [item["id"] for item in resposta.json()] == [produto["id"]]

        resposta = client.put(
            f"/produtos/{produto['id']}",
            headers=headers,
            json={"quantidade_estoque": 4},
        )
        assert resposta.status_code == 200
        assert resposta.json()["quantidade_estoque"] == 4

        resposta = client.post(
            "/vendas",
            headers=headers,
            json={"itens": [{"produto_id": produto["id"], "quantidade": 2}]},
        )
        assert resposta.status_code == 201
        venda = resposta.json()
        assert venda["valor_total"] == "39.80"
        assert venda["itens"][0]["produto_nome"] == "Caderno"
        assert venda["itens"][0]["subtotal"] == "39.80"

        resposta = client.get("/vendas", headers=headers)
        assert resposta.status_code == 200
        assert resposta.json()[0]["id"] == venda["id"]

        resposta = client.get("/produtos/estoque-baixo?limite=2", headers=headers)
        assert resposta.status_code == 200
        assert resposta.json()[0]["id"] == produto["id"]

        resposta = client.get("/dashboard/resumo?limite_estoque=2", headers=headers)
        assert resposta.status_code == 200
        assert resposta.json() == {
            "total_produtos": 1,
            "total_vendas": 1,
            "faturamento_total": "39.80",
            "produtos_estoque_baixo": 1,
            "vendas_hoje": 1,
            "faturamento_hoje": "39.80",
        }

        resposta = client.delete(f"/produtos/{produto['id']}", headers=headers)
        assert resposta.status_code == 409

        resposta = client.post(
            "/produtos",
            headers=headers,
            json={"nome": "Borracha", "preco": "3.00", "quantidade_estoque": 10},
        )
        produto_sem_vendas = resposta.json()
        resposta = client.delete(f"/produtos/{produto_sem_vendas['id']}", headers=headers)
        assert resposta.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_erros_de_venda_e_cors_para_o_frontend(db):
    client = criar_cliente(db)
    try:
        headers = criar_usuario_e_token(client)
        resposta = client.post(
            "/produtos",
            headers=headers,
            json={"nome": "Caneta", "preco": "5.00", "quantidade_estoque": 1},
        )
        produto_id = resposta.json()["id"]

        resposta = client.post(
            "/vendas",
            headers=headers,
            json={"itens": [{"produto_id": produto_id, "quantidade": 2}]},
        )
        assert resposta.status_code == 400
        assert "Estoque insuficiente" in resposta.json()["detail"]

        resposta = client.post(
            "/vendas",
            headers=headers,
            json={"itens": [{"produto_id": 999, "quantidade": 1}]},
        )
        assert resposta.status_code == 404

        resposta = client.post(
            "/vendas",
            headers=headers,
            json={"itens": [{"produto_id": produto_id, "quantidade": 0}]},
        )
        assert resposta.status_code == 422

        resposta = client.options(
            "/produtos",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resposta.status_code == 200
        assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
    finally:
        app.dependency_overrides.clear()
