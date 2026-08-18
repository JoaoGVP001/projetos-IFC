# Dashboard de Vendas e Estoque

API REST para gerenciamento de produtos, estoque, clientes, usuários e vendas.

Projeto desenvolvido com Python e FastAPI, utilizando PostgreSQL como banco de dados e Alembic para controle de migrations.

> Status: Em desenvolvimento

## Tecnologias

- Python 3.14
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- JWT
- Passlib
- OAuth2

## Funcionalidades

### Autenticação

- Cadastro de usuários
- Login com usuário e senha
- Autenticação utilizando JWT
- Proteção de endpoints
- OAuth2 Password Flow

### Produtos

CRUD completo de produtos:

- Criar produto
- Listar produtos
- Consultar produto por ID
- Atualizar produto
- Excluir produto

Cada produto possui:

- Nome
- Código de barras
- Preço
- Quantidade em estoque

Somente usuários `ADMIN` podem criar, editar e excluir produtos. Toda quantidade
inicial ou alteração de saldo gera uma movimentação de estoque.

### Estoque

- Entrada e ajuste manual de estoque
- Reserva e baixa automática em vendas
- Devolução automática no cancelamento da venda
- Histórico auditável de entradas, saídas, reservas, ajustes e devoluções

### Vendas e clientes

- Venda com múltiplos itens e preço registrado no momento da compra
- Cliente opcional vinculado à venda
- Cancelamento de venda com reversão do estoque
- Dashboard considera somente vendas concluídas no faturamento

### Permissões

- O primeiro usuário registrado recebe o perfil `ADMIN`
- Usuários posteriores recebem o perfil `OPERADOR`
- `ADMIN`: produtos, estoque e dashboard
- `OPERADOR`: vendas e clientes

### Banco de dados

O projeto utiliza PostgreSQL com SQLAlchemy.

As alterações na estrutura do banco são controladas pelo Alembic através de migrations versionadas.

# Como executar o projeto

## 1. Clonar o repositório

```bash
git clone https://github.com/JoaoGVP001/dashboard.git
```

Depois entre na pasta:

```bash
cd dashboard
```

## 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv venv
```

Ative o ambiente virtual:

```bash
venv\Scripts\activate
```

Se estiver tudo certo, o terminal ficará parecido com:

```text
(venv) C:\...\dashboard>
```

No Linux/Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar as dependências

Com a `venv` ativada:

```bash
pip install -r requirements.txt
```

## 4. Configurar o PostgreSQL

É necessário ter o PostgreSQL instalado e em execução.

Crie o banco de dados:

```sql
CREATE DATABASE dashboard_vendas;
```

O projeto espera uma conexão semelhante a:

```text
postgresql://usuario:senha@localhost:5432/dashboard_vendas
```

## 5. Configurar o arquivo `.env`

Crie um arquivo chamado:

```text
.env
```

na raiz do projeto.

Utilize o `.env.example` como referência.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/dashboard_vendas

SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Para gerar uma `SECRET_KEY` segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> Nunca envie o arquivo `.env` para o GitHub. Ele contém informações sensíveis e já está incluído no `.gitignore`.

## 6. Executar as migrations

Com o PostgreSQL rodando e a `venv` ativada:

```bash
alembic upgrade head
```

Esse comando aplica as migrations e cria ou atualiza a estrutura do banco de dados.

Para verificar se existem alterações pendentes:

```bash
alembic check
```

Quando o banco estiver atualizado, o resultado esperado será:

```text
No new upgrade operations detected.
```

## 7. Iniciar a API

Com a `venv` ativada:

```bash
uvicorn app.main:app --reload
```

Se estiver funcionando, aparecerá algo semelhante a:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

Para interromper o servidor:

```text
Ctrl + C
```

## 8. Acessar a documentação Swagger

Com o servidor rodando, abra no navegador:

```text
http://127.0.0.1:8000/docs
```

O Swagger permite testar a API diretamente pelo navegador.

### Fluxo recomendado

Primeiro registre um usuário:

```text
POST /auth/registrar
```

Depois faça login:

```text
POST /auth/login
```

O login retornará um token:

```json
{
  "access_token": "seu_token",
  "token_type": "bearer"
}
```

No Swagger, clique em:

```text
Authorize
```

Informe as credenciais solicitadas.

Depois da autorização, será possível acessar as rotas protegidas de produtos.

# Endpoints

## Autenticação

```text
POST /auth/registrar
POST /auth/login
```

## Produtos

```text
GET    /produtos?busca=termo
GET    /produtos/estoque-baixo?limite=5
POST   /produtos
GET    /produtos/{produto_id}
PUT    /produtos/{produto_id}
DELETE /produtos/{produto_id}
```

## Vendas

```text
POST /vendas
GET  /vendas
GET  /vendas/{venda_id}
POST /vendas/{venda_id}/cancelamento
```

## Clientes

```text
GET  /clientes
POST /clientes
GET  /clientes/{cliente_id}
PUT  /clientes/{cliente_id}
```

## Estoque

```text
GET  /estoque/{produto_id}
GET  /estoque/movimentacoes?produto_id=1
POST /estoque/entradas
POST /estoque/ajustes
```

## Dashboard

```text
GET /dashboard/resumo?limite_estoque=5
```

## Usuário autenticado

```text
GET /auth/me
```

## Integração com frontend

O backend permite requisições do frontend React em `http://localhost:5173`.
Configure `CORS_ORIGINS` no arquivo `.env` para adicionar outras origens, separadas por vírgula.

Após `POST /auth/login`, envie o token em todas as rotas protegidas:

```text
Authorization: Bearer SEU_TOKEN
```

Exemplo de criação de venda:

```json
{
  "itens": [
    {"produto_id": 1, "quantidade": 2},
    {"produto_id": 5, "quantidade": 1}
  ]
}
```

## Status

```text
GET /
```

Retorno:

```json
{
  "status": "online"
}
```

# Migrations

O projeto utiliza Alembic para controlar a evolução do banco de dados.

## Criar uma nova migration

Depois de alterar algum modelo SQLAlchemy:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

## Aplicar migrations

```bash
alembic upgrade head
```

## Verificar alterações pendentes

```bash
alembic check
```

## Voltar uma migration

```bash
alembic downgrade -1
```

As migrations ficam armazenadas em:

```text
alembic/versions/
```

Esses arquivos devem ser versionados pelo Git.

# Fluxo de autenticação

```text
Usuário
   │
   ├── POST /auth/registrar
   │
   └── POST /auth/login
             │
             ▼
       Access Token JWT
             │
             ▼
    Authorization: Bearer
             │
             ▼
      Rotas protegidas
             │
             ▼
        Produtos
```

# Roadmap

## Concluído

* [x] Estrutura inicial da API
* [x] FastAPI
* [x] PostgreSQL
* [x] SQLAlchemy
* [x] Pydantic
* [x] Configuração por variáveis de ambiente
* [x] Autenticação de usuários
* [x] JWT
* [x] OAuth2 Password Flow
* [x] CRUD de produtos
* [x] Documentação Swagger
* [x] Alembic
* [x] Configuração de migrations
* [x] Migration inicial
* [x] Remoção do `Base.metadata.create_all()`

## Em desenvolvimento

### Vendas

* [x] Registro de vendas e itens
* [x] Baixa automática e cancelamento com devolução
* [x] Histórico das vendas
* [x] Cadastro e vínculo opcional de clientes

### Estoque

* [x] Registrar movimentações de estoque
* [x] Histórico de entradas e saídas
* [ ] Controle de estoque mínimo
* [ ] Relatório de estoque baixo
* [x] Controle de ajustes de estoque

### Relatórios

* [ ] Vendas por período
* [ ] Faturamento por período
* [ ] Produtos mais vendidos
* [ ] Faturamento diário
* [ ] Ticket médio
* [ ] Relatórios de estoque
* [ ] Produtos com estoque baixo

### Frontend

* [ ] Criar interface web
* [ ] Tela de login
* [ ] Dashboard
* [ ] Gerenciamento de produtos
* [ ] Gerenciamento de vendas
* [ ] Visualização de estoque
* [ ] Gráficos e indicadores

# Objetivo

O objetivo do projeto é desenvolver uma aplicação completa de gestão de vendas e estoque.

O projeto começa como uma API REST e será evoluído para uma aplicação completa contendo:

* Autenticação
* Gerenciamento de produtos
* Controle de estoque
* Registro de vendas
* Relatórios
* Dashboard
* Interface gráfica

A arquitetura foi estruturada de forma modular para permitir a evolução da aplicação conforme novas funcionalidades forem implementadas.

# Desenvolvimento

Durante o desenvolvimento, recomenda-se manter o ambiente virtual ativado:

```bash
venv\Scripts\activate
```

Iniciar a API:

```bash
uvicorn app.main:app --reload
```

Verificar migrations:

```bash
alembic check
```

Criar migration após alterações nos modelos:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
```

Aplicar migration:

```bash
alembic upgrade head
```

# Estrutura do projeto

```text
dashboard-vendas/
│
├── alembic/
│   └── versions/
│       └── migrations do banco
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── usuario.py
│   │   └── produto.py
│   │
│   ├── schemas/
│   │   ├── usuario.py
│   │   └── produto.py
│   │
│   ├── crud/
│   │   ├── usuario.py
│   │   └── produto.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   └── produtos.py
│   │
│   └── main.py
│
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

# Licença

Projeto desenvolvido para fins de estudo e desenvolvimento acadêmico.
