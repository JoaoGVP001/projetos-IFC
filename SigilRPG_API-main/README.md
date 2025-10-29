# API para RPG básico - Flask

Uma API pequena que fornece dados JSON via HTTP para ser consumida por um aplicativo frontend ou outros serviços.

Esta é uma conversão da API Laravel/Lumen original para Flask, mantendo todas as funcionalidades principais.

## Funcionalidades

- **Autenticação JWT**: Login, refresh de token e logout
- **Gestão de Personagens**: Listar todos os personagens e mostrar detalhes
- **Personagem do Usuário**: Criar e gerenciar personagem do usuário logado
- **Sistema de Lutas**: Criar lutas e listar lutas do usuário

## Configuração Rápida

1. Clone este repositório ou baixe o arquivo
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure suas variáveis de ambiente:
   - Copie `env_example.txt` para `.env`
   - Atualize as configurações conforme necessário
4. Execute o script de dados iniciais:
   ```bash
   python seed_data.py
   ```
5. Execute a aplicação:
   ```bash
   python app.py
   ```

## Executando a API

```bash
python app.py
```

A API estará disponível em `http://localhost:8000`

## Endpoints da API

### Autenticação

#### Login de Usuário
Para autenticar um usuário, faça uma requisição `POST` para `/api/auth/login` com os parâmetros:

```json
{
  "email": "joao@example.com",
  "password": "123456"
}
```

**Resposta:**
```json
{
  "message": "token_generated",
  "data": {
    "token": "um_token_longo_aqui"
  }
}
```

Para todas as requisições que requerem login, use o token no header:
```
Authorization: Bearer {token_aqui}
```

#### Ver Usuário Autenticado
**Requisição:** `GET /api/auth/user` com token de autenticação

#### Atualizar Token
**Requisição:** `PATCH /api/auth/` com token de autenticação

#### Invalidar Token
**Requisição:** `DELETE /api/auth/` com token de autenticação

### Personagens

#### Explorar Todos os Personagens
**Requisição:** `GET /api/characters` para ver lista de todos os personagens
**Requisição:** `GET /api/characters/{characterId}` para ver detalhes de um personagem específico

#### Criar um Personagem
**Requisição:** `POST /api/me/` com token de autenticação para criar o personagem do usuário

**Parâmetros:**
```json
{
  "name": "Nome do Personagem",
  "age": 25,
  "skilled_in": "Espada e Escudo"
}
```

#### Ver Personagem do Usuário
**Requisição:** `GET /api/me/` para ver informações do personagem do usuário atual

### Lutas

#### Criar Nova Luta
**Requisição:** `POST /api/me/fights/` com token de autenticação para criar uma luta

**Parâmetros:**
```json
{
  "opponent_id": 3
}
```

#### Listar Lutas do Usuário
**Requisição:** `GET /api/me/fights/` com token de autenticação para listar as lutas do personagem do usuário atual

## Exemplos de Uso

### Login
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"joao@example.com","password":"123456"}' \
  http://localhost:8000/api/auth/login
```

### Listar Personagens
```bash
curl http://localhost:8000/api/characters
```

### Criar Personagem (com autenticação)
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"name":"Meu Personagem","age":30,"skilled_in":"Magia"}' \
  http://localhost:8000/api/me/
```

### Criar Luta (com autenticação)
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"opponent_id":3}' \
  http://localhost:8000/api/me/fights/
```

## Estrutura do Projeto

```
REST-API-for-basic-RPG-flask/
├── app.py                 # Aplicação principal Flask
├── models.py             # Modelos SQLAlchemy
├── routes.py             # Rotas de autenticação
├── characters_routes.py  # Rotas de personagens
├── user_character_routes.py # Rotas do personagem do usuário
├── fights_routes.py      # Rotas de lutas
├── seed_data.py          # Script para dados iniciais
├── requirements.txt      # Dependências Python
└── env_example.txt       # Exemplo de configuração
```

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Migrate**: Migrações de banco de dados
- **Werkzeug**: Utilitários de segurança

## Banco de Dados

A API usa SQLite por padrão, mas pode ser facilmente configurada para usar MySQL, PostgreSQL ou outros bancos suportados pelo SQLAlchemy.

## Notas Importantes

- O jogo é persistente, então o usuário pode fazer login a qualquer momento e retomar o jogo de onde parou
- Quando uma luta é completada, cada luta do usuário tem registro dos pontos de experiência
- Uma luta pode ter diferentes pontos de experiência dependendo do resultado da luta
- A experiência está registrada em cada registro de luta do usuário e pode ser usada para relatórios ou outros propósitos conforme o jogo progride


