# Dashboard de Vendas e Estoque — API

Estrutura inicial com **FastAPI + SQLAlchemy + Pydantic + Passlib + PostgreSQL**.

## Estrutura de pastas

```
dashboard-vendas/
├── app/
│   ├── core/           # configurações, conexão com banco, segurança/JWT
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── deps.py
│   ├── models/         # modelos SQLAlchemy (tabelas do banco)
│   │   ├── usuario.py
│   │   └── produto.py
│   ├── schemas/        # modelos Pydantic (validação de entrada/saída)
│   │   ├── usuario.py
│   │   └── produto.py
│   ├── crud/           # funções que conversam com o banco
│   │   ├── usuario.py
│   │   └── produto.py
│   ├── routers/         # rotas da API
│   │   ├── auth.py
│   │   └── produtos.py
│   └── main.py          # ponto de entrada
├── requirements.txt
├── .env.example
└── README.md
```

## Como rodar

### 1. Criar e ativar um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Criar o banco no PostgreSQL

```sql
CREATE DATABASE dashboard_vendas;
```

### 4. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores (usuário, senha, host, e uma `SECRET_KEY` aleatória):

```bash
cp .env.example .env
```

Para gerar uma SECRET_KEY aleatória boa, rode:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Rodar a aplicação

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`.
A documentação interativa (Swagger) fica em `http://127.0.0.1:8000/docs` — dá pra testar registro, login e as rotas de produto direto pelo navegador, sem precisar de Postman.

## Fluxo de uso

1. `POST /auth/registrar` — cria um usuário (username, email, senha)
2. `POST /auth/login` — envia username + senha, recebe um `access_token`
3. Use esse token no botão **Authorize** do `/docs` (ou no header `Authorization: Bearer <token>`) para acessar as rotas de `/produtos`, que exigem login

## Próximos passos sugeridos

- Trocar a criação automática de tabelas (`Base.metadata.create_all`) por **Alembic** (migrations versionadas) — já está no requirements.txt
- Adicionar um modelo de **Vendas** relacionando Produto + quantidade + data
- Criar rotas de relatório (ex: produtos com estoque baixo, vendas por período)
- Conectar um frontend (React, ou até Streamlit separado) consumindo essa API
