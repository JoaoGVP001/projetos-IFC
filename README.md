# SIGIL RPG - Sistema de Gerenciamento de Personagens

Um sistema completo para criação e gerenciamento de personagens do sistema Sigil RPG, com backend FastAPI e frontend Flutter, incluindo autenticação JWT e controle de personagens por usuário.

## ✅ Atualizações Implementadas

- Autenticação antes de criar personagens usando `AuthService` (fluxo de criação exige login).
- Personagens do usuário agora usam `getUserCharacter()` em vez de `fetchCharacters()`.
- Telas de Login e Registro adicionadas e integradas (`/auth/login`, `/auth/register`).
- UI de Lutas criada e integrada com `FightsService` (rota `/fights`).

### Como usar no App

- Acesse Menu → botão de Login no AppBar ou vá em `Entrar` para autenticar.
- Para criar personagem: após logar, use Home → Personagens → Criar Personagem.
- Para ver seu personagem: Home → Personagens → Meus Personagens (carrega seu personagem autenticado).
- Para Lutas: Home → Combate → Lutas (listar histórico e iniciar luta por ID de oponente).

### Endpoints usados no Frontend

- Auth: `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/user`, `PATCH/DELETE /api/auth/` (refresh/logout)
- Personagem do usuário: `GET /api/me/`, `POST /api/me/`
- Lutas do usuário: `GET /api/me/fights/`, `POST /api/me/fights/`

## 🚀 Funcionalidades

### Backend (FastAPI)
- **Autenticação JWT**: Sistema completo de login/registro com tokens JWT
- **Gerenciamento de Usuários**: Criação, autenticação e sessões persistentes
- **CRUD de Personagens**: Criação, listagem, atualização e exclusão
- **Controle de Acesso**: Apenas donos podem ver/editar seus personagens
- **API RESTful**: Endpoints organizados com validação de dados
- **Sistema Sigil**: Atributos específicos (Agilidade, Intelecto, Vigor, Presença, Força)

### Frontend (Flutter)
- **Sistema de Login/Registro**: Interface completa de autenticação
- **Criação de Personagens**: Fluxo multi-etapas (Básico → Origem → Classe → Detalhes)
- **Edição de Atributos**: Tela dedicada para ajustar atributos pós-criação
- **Gerenciamento de Sessão**: Persistência de login com SharedPreferences
- **Interface Responsiva**: Design moderno com Material Design 3

## 🏗️ Arquitetura

### Backend (Python/FastAPI) - Nova Estrutura
```
app/
├── core/
│   ├── config.py              # Configurações da aplicação
│   ├── database.py            # Configuração do banco de dados
│   └── security.py            # Segurança e JWT
├── models/
│   ├── user.py                # Modelo de usuário
│   └── character.py           # Modelo de personagem (Sistema Sigil)
├── schemas/
│   ├── user.py                # Schemas de usuário
│   ├── character.py           # Schemas de personagem
│   └── token.py               # Schemas de token JWT
├── crud/
│   ├── user.py                # Operações CRUD de usuários
│   └── character.py           # Operações CRUD de personagens
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py        # Endpoints de autenticação
│           └── characters.py   # Endpoints de personagens
└── main.py                    # Aplicação principal
```

### Frontend (Flutter)
```
lib/
├── constants/
│   ├── app_colors.dart        # Paleta de cores
│   ├── app_routes.dart        # Definição de rotas
│   └── app_theme.dart         # Tema da aplicação
├── controllers/
│   ├── auth_controller.dart   # Controle de autenticação
│   ├── characters_controller.dart # Controle de personagens
│   ├── character_draft_controller.dart # Controle de criação
│   ├── campaigns_controller.dart # Controle de campanhas
│   ├── teams_controller.dart  # Controle de times
│   └── dicecontroller.dart    # Controle de dados
├── models/
│   ├── character.dart         # Modelo de personagem
│   ├── character_class.dart   # Classes de personagem
│   ├── character_origin.dart  # Origens de personagem
│   ├── campaign.dart          # Modelo de campanha
│   ├── item.dart             # Modelo de item
│   └── user.dart             # Modelo de usuário
├── services/
│   ├── auth_service.dart      # Serviço de autenticação
│   └── characters_service.dart # Serviço de personagens
├── utils/
│   ├── api.dart              # Cliente HTTP com autenticação
│   └── dice.dart             # Utilitários de dados
├── views/
│   ├── auth/
│   │   ├── login_view.dart    # Tela de login
│   │   └── register_view.dart # Tela de registro
│   ├── characters/
│   │   ├── characters_list_view.dart # Lista de personagens
│   │   ├── character_create_basics_view.dart # Criação - Básico
│   │   ├── character_create_origin_view.dart # Criação - Origem
│   │   ├── character_create_class_view.dart # Criação - Classe
│   │   ├── character_create_details_view.dart # Criação - Detalhes
│   │   ├── character_attributes_edit_view.dart # Edição de atributos
│   │   └── character_detail_view.dart # Detalhes do personagem
│   ├── campaigns/
│   │   └── campaigns_view.dart # Gerenciamento de campanhas
│   ├── teams/
│   │   └── teams_view.dart    # Gerenciamento de times
│   ├── dice/
│   │   └── dice_view.dart     # Rolagem de dados
│   └── home/
│       └── home_view.dart     # Tela inicial
├── widgets/
│   ├── character_card.dart    # Card de personagem
│   ├── attribute_circle.dart # Círculo de atributo
│   ├── health_bar.dart        # Barra de vida
│   ├── skill_row.dart         # Linha de habilidade
│   └── dice_roller.dart       # Rolador de dados
└── main.dart                  # Aplicação principal
```

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validação de dados
- **JWT**: Autenticação com tokens (python-jose)
- **Bcrypt**: Hash de senhas (passlib)
- **Uvicorn**: Servidor ASGI

### Frontend
- **Flutter**: Framework de UI multiplataforma
- **Provider**: Gerenciamento de estado
- **HTTP**: Cliente para APIs
- **SharedPreferences**: Persistência local
- **Material Design 3**: Design system

## 📋 Endpoints da API

### Autenticação (`/api/v1/auth/`)
- `POST /register` - Registrar novo usuário
  - Body: `{username, email, password, full_name?}`
  - Response: `{id, username, email, full_name, created_at}`
  
- `POST /login` - Login de usuário
  - Body: `{username, password}`
  - Response: `{access_token, token_type}`

- `GET /me` - Obter dados do usuário atual
  - Headers: `Authorization: Bearer <token>`
  - Response: `{id, username, email, full_name, is_active, created_at}`

- `POST /refresh` - Renovar token JWT
  - Headers: `Authorization: Bearer <token>`
  - Response: `{access_token, token_type}`

### Personagens (`/api/v1/characters/`)
- `GET /` - Listar personagens do usuário autenticado
  - Headers: `Authorization: Bearer <token>`
  - Response: `[{id, name, player_name, origin, character_class, nex, ...}]`

- `GET /{id}` - Obter personagem específico
  - Headers: `Authorization: Bearer <token>`
  - Response: `{id, name, player_name, origin, character_class, nex, ...}`

- `POST /` - Criar novo personagem
  - Headers: `Authorization: Bearer <token>`
  - Body: `{name, player_name, origin, character_class, nex, agilidade, intelecto, vigor, presenca, forca, ...}`
  - Response: `{id, name, player_name, origin, character_class, nex, ...}`

- `PATCH /{id}` - Atualizar personagem parcialmente
  - Headers: `Authorization: Bearer <token>`
  - Body: `{name?, player_name?, origin?, character_class?, nex?, agilidade?, ...}`
  - Response: `{id, name, player_name, origin, character_class, nex, ...}`

- `DELETE /{id}` - Excluir personagem
  - Headers: `Authorization: Bearer <token>`
  - Response: `204 No Content`

## 🎮 Sistema Sigil RPG

### Atributos do Personagem
- **Agilidade**: Valor entre 0 e 3
- **Intelecto**: Valor entre 0 e 3
- **Vigor**: Valor entre 0 e 3
- **Presença**: Valor entre 0 e 3
- **Força**: Valor entre 0 e 3
- **NEX**: Valor entre 5 e 99

### Validações
- **Username**: Mínimo 3 caracteres, único
- **Email**: Formato válido, único
- **Password**: Mínimo 6 caracteres
- **Atributos**: Valores entre 0 e 3
- **NEX**: Valores entre 5 e 99

## 🔐 Sistema de Autenticação

- **Registro**: Username, email, senha, nome completo (opcional)
- **Login**: Username + senha
- **Sessão Persistente**: Token JWT salvo localmente
- **Controle de Acesso**: Apenas donos podem ver/editar seus personagens
- **Autorização**: Bearer token em todas as requisições autenticadas

## 🚀 Como Executar

### Backend

1. **Instalar dependências**:
```bash
cd app
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente**:
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
DATABASE_URL=sqlite:///./sigilrpg.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Inicializar banco de dados**:
```bash
python create_db.py
```

4. **Executar servidor**:
```bash
# Opção 1: Usando uvicorn diretamente
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2: Usando script personalizado
python run_server.py
```

### Frontend

1. **Instalar dependências**:
```bash
flutter pub get
```

2. **Executar aplicação**:
```bash
# Web
flutter run -d chrome

# Android
flutter run

# iOS (apenas no macOS)
flutter run -d ios
```

## 📱 Funcionalidades do App

### Autenticação
- Login com username/email
- Registro de novos usuários
- Logout automático
- Sessão persistente com JWT

### Personagens
- Criação em etapas (Básico → Origem → Classe → Detalhes)
- Edição de atributos pós-criação
- Controle de acesso (apenas donos)
- Listagem de personagens do usuário

### Interface
- Design responsivo
- Navegação intuitiva
- Feedback visual
- Validação de formulários

## 🔧 Configuração de Desenvolvimento

### Backend
- **Porta**: 8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Frontend
- **Web**: http://localhost:8000 (conecta automaticamente)
- **Android Emulator**: http://10.0.2.2:8000
- **iOS Simulator**: http://localhost:8000

## 📊 Exemplos de Uso

### Registro de Usuário
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jogador1",
    "email": "jogador@email.com",
    "password": "senha123",
    "full_name": "João Silva"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jogador1",
    "password": "senha123"
  }'
```

### Criar Personagem
```bash
curl -X POST "http://localhost:8000/api/v1/characters" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Alex Silva",
    "player_name": "João Silva",
    "origin": "Cultista",
    "character_class": "Ocultista",
    "nex": 15,
    "agilidade": 2,
    "intelecto": 3,
    "vigor": 1,
    "presenca": 2,
    "forca": 1
  }'
```

## 🔮 Próximas Funcionalidades

- [ ] Sistema de campanhas completo
- [ ] Gerenciamento de itens
- [ ] Sistema de dados avançado
- [ ] Compartilhamento de personagens
- [ ] Sistema de notificações
- [ ] Modo offline
- [ ] Sincronização em tempo real

## 📄 Licença

Este projeto é privado e desenvolvido para fins educacionais e pessoais.

## 👥 Contribuição

Para contribuir com o projeto, entre em contato com os desenvolvedores.

---

**SIGIL RPG** - Sistema completo de gerenciamento de personagens do sistema Sigil RPG com autenticação JWT e controle de acesso por usuário.