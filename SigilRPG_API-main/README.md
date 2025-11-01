# API para RPG básico - Flask (SIGIL RPG)

Uma API RESTful completa que fornece dados JSON via HTTP para ser consumida por aplicativos Flutter ou outros frontends.

Esta é uma conversão da API Laravel/Lumen original para Flask, mantendo todas as funcionalidades principais e melhorada com suporte completo para o sistema Sigil RPG.

## 🎯 Funcionalidades

- **Autenticação JWT**: Login, registro, refresh de token e logout
- **Gestão de Personagens**: CRUD completo de personagens
- **Personagem do Usuário**: Criar e gerenciar personagem do usuário logado
- **Sistema de Lutas**: Criar lutas e listar histórico de lutas
- **Sistema Sigil RPG**: Atributos, NEX, origens, classes e detalhes completos

## ✅ Atualizações Recentes

### Correções de Bugs
- ✅ **Bug do NEX**: Corrigido problema onde personagens eram criados com NEX 0
- ✅ **Campos Opcionais**: Todos os campos opcionais agora são salvos corretamente na criação

### Melhorias
- ✅ Suporte completo para todos os atributos do personagem (Agilidade, Intelecto, Vigor, Presença, Força)
- ✅ Campos de detalhes do personagem (gênero, aparência, personalidade, histórico, objetivo)
- ✅ Suporte para origem e classe do personagem
- ✅ Avatar URL suportado

## 🚀 Configuração Rápida

1. Clone este repositório ou baixe o arquivo
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure suas variáveis de ambiente:
   - Copie `env_example.txt` para `.env`
   - Atualize as configurações conforme necessário
4. Execute o script de migração (se necessário):
   ```bash
   python migrate_db.py
   ```
5. Execute o script de dados iniciais (opcional):
   ```bash
   python seed_data.py
   ```
6. Execute a aplicação:
   ```bash
   python app.py
   ```

## Executando a API

```bash
python app.py
```

A API estará disponível em `http://localhost:8000`

- **Swagger UI**: `http://localhost:8000/docs` (se configurado)
- **Health Check**: `http://localhost:8000/`

## 📋 Endpoints da API

### Autenticação

#### Registrar Novo Usuário
**Requisição:** `POST /api/auth/register`

**Parâmetros:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "123456"
}
```

**Resposta:**
```json
{
  "message": "user_created",
  "data": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

#### Login de Usuário
**Requisição:** `POST /api/auth/login`

**Parâmetros:**
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

**Para todas as requisições que requerem login, use o token no header:**
```
Authorization: Bearer {token_aqui}
```

#### Ver Usuário Autenticado
**Requisição:** `GET /api/auth/user` (com token de autenticação)

**Resposta:**
```json
{
  "message": "user",
  "data": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com"
  }
}
```

#### Atualizar Token
**Requisição:** `PATCH /api/auth/` (com token de autenticação)

#### Invalidar Token
**Requisição:** `DELETE /api/auth/` (com token de autenticação)

### Personagens do Sistema

#### Listar Todos os Personagens
**Requisição:** `GET /api/characters`

**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Alex Silva",
    "player_name": "João",
    "nex": 15,
    "origin": "Cultista",
    "character_class": "Ocultista",
    ...
  }
]
```

#### Ver Detalhes de um Personagem
**Requisição:** `GET /api/characters/{characterId}`

#### Criar um Personagem (Sistema)
**Requisição:** `POST /api/characters`

**Parâmetros:**
```json
{
  "name": "Nome do Personagem",
  "player_name": "Nome do Jogador",
  "age": 25,
  "nex": 15,
  "origin": "Cultista",
  "character_class": "Ocultista",
  "skilled_in": "Espada e Escudo",
  "agilidade": 2,
  "intelecto": 3,
  "vigor": 1,
  "presenca": 2,
  "forca": 1
}
```

### Personagem do Usuário

#### Criar Personagem do Usuário
**Requisição:** `POST /api/me/` (com token de autenticação)

**Campos Obrigatórios:**
- `name`: Nome do personagem (string, obrigatório)
- `age`: Idade (integer, entre 1 e 200, obrigatório)
- `skilled_in`: Habilidade especial (string, obrigatório)

**Campos Opcionais:**
- `player_name`: Nome do jogador (string)
- `origin`: Origem do personagem (string)
- `character_class`: Classe do personagem (string)
- `nex`: NEX do personagem (integer, padrão: 5, entre 5-100)
- `avatar_url`: URL do avatar (string)
- `agilidade`: Agilidade (integer, padrão: 1, entre 0-3)
- `intelecto`: Intelecto (integer, padrão: 1, entre 0-3)
- `vigor`: Vigor (integer, padrão: 1, entre 0-3)
- `presenca`: Presença (integer, padrão: 1, entre 0-3)
- `forca`: Força (integer, padrão: 1, entre 0-3)
- `gender`: Gênero (string)
- `appearance`: Aparência (string)
- `personality`: Personalidade (string)
- `background`: Histórico (string)
- `objective`: Objetivo (string)

**Exemplo Completo:**
```json
{
  "name": "Alex Silva",
  "player_name": "João Silva",
  "age": 25,
  "nex": 15,
  "origin": "Cultista",
  "character_class": "Ocultista",
  "skilled_in": "Rituais",
  "avatar_url": "https://example.com/avatar.jpg",
  "agilidade": 2,
  "intelecto": 3,
  "vigor": 1,
  "presenca": 2,
  "forca": 1,
  "gender": "Masculino",
  "appearance": "Alto e magro",
  "personality": "Determinado",
  "background": "Ex-investigador",
  "objective": "Proteger a Ordem"
}
```

**Resposta:**
```json
{
  "message": "character_created",
  "data": {
    "id": 1,
    "name": "Alex Silva",
    "nex": 15,
    "origin": "Cultista",
    "character_class": "Ocultista",
    ...
  }
}
```

#### Ver Personagem do Usuário
**Requisição:** `GET /api/me/` (com token de autenticação)

**Resposta:**
```json
{
  "message": "character",
  "data": {
    "id": 1,
    "name": "Alex Silva",
    "nex": 15,
    ...
  }
}
```

### Lutas

#### Criar Nova Luta
**Requisição:** `POST /api/me/fights/` (com token de autenticação)

**Parâmetros:**
```json
{
  "opponent_id": 3
}
```

**Resposta:**
```json
{
  "message": "fight_created",
  "data": {
    "id": 1,
    "opponent_id": 3,
    "character_id": 1,
    "status": "won",
    "experience": 100
  }
}
```

#### Listar Lutas do Usuário
**Requisição:** `GET /api/me/fights/` (com token de autenticação)

**Resposta:**
```json
{
  "message": "fights",
  "data": [
    {
      "id": 1,
      "opponent_id": 3,
      "status": "won",
      "experience": 100,
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

## 📖 Exemplos de Uso

### Login
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"joao@example.com","password":"123456"}' \
  http://localhost:8000/api/auth/login
```

### Registrar Usuário
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"João Silva","email":"joao@example.com","password":"123456"}' \
  http://localhost:8000/api/auth/register
```

### Listar Personagens
```bash
curl http://localhost:8000/api/characters
```

### Criar Personagem do Usuário (com autenticação)
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "name": "Alex Silva",
    "player_name": "João Silva",
    "age": 25,
    "nex": 15,
    "origin": "Cultista",
    "character_class": "Ocultista",
    "skilled_in": "Rituais",
    "agilidade": 2,
    "intelecto": 3,
    "vigor": 1,
    "presenca": 2,
    "forca": 1
  }' \
  http://localhost:8000/api/me/
```

### Ver Personagem do Usuário
```bash
curl -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  http://localhost:8000/api/me/
```

### Criar Luta (com autenticação)
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"opponent_id":3}' \
  http://localhost:8000/api/me/fights/
```

## 🏗️ Estrutura do Projeto

```
SigilRPG_API-main/
├── app.py                      # Aplicação principal Flask
├── models.py                   # Modelos SQLAlchemy (User, Character, Fight)
├── routes.py                   # Rotas de autenticação
├── characters_routes.py        # Rotas de personagens do sistema
├── user_character_routes.py    # Rotas do personagem do usuário
├── fights_routes.py            # Rotas de lutas
├── config.py                   # Configurações (se houver)
├── migrate_db.py               # Script de migração do banco
├── seed_data.py                # Script para dados iniciais
├── requirements.txt            # Dependências Python
├── env_example.txt             # Exemplo de configuração
└── instance/
    └── rpg.db                  # Banco de dados SQLite (gerado automaticamente)
```

## 🔧 Tecnologias Utilizadas

- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Migrate**: Migrações de banco de dados
- **Flask-CORS**: Suporte para CORS (Cross-Origin Resource Sharing)
- **Werkzeug**: Utilitários de segurança (hash de senhas)

## 💾 Banco de Dados

A API usa SQLite por padrão (`sqlite:///rpg.db`), mas pode ser facilmente configurada para usar MySQL, PostgreSQL ou outros bancos suportados pelo SQLAlchemy através da variável de ambiente `DATABASE_URL`.

### Estrutura das Tabelas

**users:**
- `id` (Integer, PK)
- `name` (String)
- `email` (String, unique)
- `password_hash` (String)
- `remember_token` (String)
- `created_at`, `updated_at` (DateTime)

**characters:**
- `id` (Integer, PK)
- `name` (String)
- `player_name` (String, nullable)
- `age` (Integer)
- `skilled_in` (String)
- `character_class` (String, nullable)
- `nex` (Integer, default: 0)
- `avatar_url` (String, nullable)
- `agilidade`, `intelecto`, `vigor`, `presenca`, `forca` (Integer, default: 1)
- `gender`, `appearance`, `personality`, `background`, `objective` (Text, nullable)
- `origin` (String, nullable)
- `user_id` (Integer, FK para users)
- `created_at`, `updated_at` (DateTime)

**fights:**
- `id` (Integer, PK)
- `opponent_id` (Integer, FK)
- `character_id` (Integer, FK)
- `status` (Enum: 'won', 'lost', 'draw')
- `experience` (Integer)
- `created_at`, `updated_at` (DateTime)

## 🎮 Sistema Sigil RPG

### Atributos do Personagem
- **Agilidade** (AGI): 0-3
- **Intelecto** (INT): 0-3
- **Vigor** (VIG): 0-3
- **Presença** (PRE): 0-3
- **Força** (FOR): 0-3

### NEX (Nível de Exposição)
- Valor entre **5 e 99** (padrão: 5)
- Representa o nível de exposição ao paranormal do personagem

### Validações
- **Nome**: Obrigatório, máximo 255 caracteres
- **Idade**: Obrigatório, entre 1 e 200
- **Habilidade (skilled_in)**: Obrigatório, máximo 255 caracteres
- **Atributos**: Entre 0 e 3 cada
- **NEX**: Entre 5 e 99

## 📝 Notas Importantes

- ✅ O jogo é persistente, então o usuário pode fazer login a qualquer momento e retomar o jogo de onde parou
- ✅ Quando uma luta é completada, cada luta do usuário tem registro dos pontos de experiência
- ✅ Uma luta pode ter diferentes pontos de experiência dependendo do resultado
- ✅ A experiência está registrada em cada registro de luta do usuário
- ✅ Cada usuário pode ter apenas **um personagem** associado
- ✅ O NEX padrão é **5** se não fornecido (mínimo do sistema)
- ✅ Todos os campos opcionais são salvos corretamente na criação do personagem

## 🔐 Segurança

- Senhas são armazenadas com hash usando Werkzeug
- Tokens JWT expiram após 24 horas
- CORS configurado para permitir requisições do frontend
- Validação de dados em todos os endpoints

## 🐛 Correções Recentes

### v1.1.0
- ✅ Corrigido bug onde personagens eram criados com NEX 0
- ✅ Adicionado suporte para todos os campos opcionais na criação
- ✅ Valor padrão de NEX alterado para 5 (mínimo do sistema)
- ✅ Documentação atualizada com exemplos completos

## 📄 Licença

Este projeto é privado e desenvolvido para fins educacionais e pessoais.

---

**API SIGIL RPG** - Sistema completo de gerenciamento de personagens com autenticação JWT e suporte completo ao sistema Sigil RPG.
