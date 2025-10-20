# SIGIL RPG - Sistema de Gerenciamento de Personagens

Um sistema completo para criação e gerenciamento de personagens de RPG, com backend FastAPI e frontend Flutter, incluindo autenticação de usuários e controle de visibilidade (público/privado) dos personagens.

## 🚀 Funcionalidades

### Backend (FastAPI)
- **Autenticação JWT**: Sistema completo de login/registro com tokens JWT
- **Gerenciamento de Usuários**: Criação, autenticação e sessões persistentes
- **CRUD de Personagens**: Criação, listagem, atualização e exclusão
- **Controle de Visibilidade**: Personagens públicos/privados por usuário
- **API RESTful**: Endpoints organizados com validação de dados

### Frontend (Flutter)
- **Sistema de Login/Registro**: Interface completa de autenticação
- **Criação de Personagens**: Fluxo multi-etapas (Básico → Origem → Classe → Detalhes)
- **Edição de Atributos**: Tela dedicada para ajustar atributos pós-criação
- **Gerenciamento de Sessão**: Persistência de login com SharedPreferences
- **Interface Responsiva**: Design moderno com Material Design 3

## 🏗️ Arquitetura

### Backend (Python/FastAPI)
```
app/
├── config/
│   ├── database.py          # Configuração do banco de dados
│   ├── settings.py          # Configurações da aplicação
│   └── redis_client.py      # Cliente Redis (cache)
├── models/
│   ├── user.py              # Modelo de usuário
│   ├── character.py         # Modelo de personagem
│   ├── campaign.py          # Modelo de campanha
│   └── item.py              # Modelo de item
├── schemas/
│   ├── auth.py              # Schemas de autenticação
│   ├── user.py              # Schemas de usuário
│   ├── character.py         # Schemas de personagem
│   ├── campaign.py          # Schemas de campanha
│   └── item.py              # Schemas de item
├── services/
│   ├── auth_service.py      # Lógica de autenticação
│   ├── user_service.py      # Lógica de usuários
│   ├── character_service.py # Lógica de personagens
│   ├── campaign_service.py  # Lógica de campanhas
│   └── item_service.py      # Lógica de itens
├── routes/
│   ├── auth.py              # Endpoints de autenticação
│   ├── users.py             # Endpoints de usuários
│   ├── characters.py        # Endpoints de personagens
│   ├── campaigns.py         # Endpoints de campanhas
│   └── items.py             # Endpoints de itens
└── main.py                  # Aplicação principal
```

### Frontend (Flutter)
```
lib/
├── constants/
│   ├── app_colors.dart      # Paleta de cores
│   ├── app_routes.dart      # Definição de rotas
│   └── app_theme.dart       # Tema da aplicação
├── controllers/
│   ├── auth_controller.dart # Controle de autenticação
│   ├── characters_controller.dart # Controle de personagens
│   ├── character_draft_controller.dart # Controle de criação
│   ├── campaigns_controller.dart # Controle de campanhas
│   ├── teams_controller.dart # Controle de times
│   └── dicecontroller.dart  # Controle de dados
├── models/
│   ├── character.dart       # Modelo de personagem
│   ├── character_class.dart # Classes de personagem
│   ├── character_origin.dart # Origens de personagem
│   ├── campaign.dart        # Modelo de campanha
│   ├── item.dart           # Modelo de item
│   └── user.dart           # Modelo de usuário
├── services/
│   ├── auth_service.dart    # Serviço de autenticação
│   └── characters_service.dart # Serviço de personagens
├── utils/
│   ├── api.dart            # Cliente HTTP com autenticação
│   └── dice.dart           # Utilitários de dados
├── views/
│   ├── auth/
│   │   ├── login_view.dart # Tela de login
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
│   │   └── teams_view.dart # Gerenciamento de times
│   ├── dice/
│   │   └── dice_view.dart # Rolagem de dados
│   └── home/
│       └── home_view.dart # Tela inicial
├── widgets/
│   ├── character_card.dart # Card de personagem
│   ├── attribute_circle.dart # Círculo de atributo
│   ├── health_bar.dart # Barra de vida
│   ├── skill_row.dart # Linha de habilidade
│   └── dice_roller.dart # Rolador de dados
└── main.dart # Aplicação principal
```

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validação de dados
- **JWT**: Autenticação com tokens
- **Bcrypt**: Hash de senhas
- **Uvicorn**: Servidor ASGI

### Frontend
- **Flutter**: Framework de UI multiplataforma
- **Provider**: Gerenciamento de estado
- **HTTP**: Cliente para APIs
- **SharedPreferences**: Persistência local
- **Material Design 3**: Design system

## 📋 Endpoints da API

### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Dados do usuário atual
- `POST /api/v1/auth/refresh` - Renovar token

### Personagens
- `GET /api/v1/characters` - Listar personagens públicos
- `GET /api/v1/characters/mine` - Listar meus personagens (autenticado)
- `POST /api/v1/characters` - Criar personagem (autenticado)
- `GET /api/v1/characters/{id}` - Obter personagem por ID
- `PATCH /api/v1/characters/{id}` - Atualizar personagem (apenas dono)

## 🎮 Fluxo de Criação de Personagem

1. **Informações Básicas**: Nome, jogador, NEX, avatar
2. **Origem**: Escolha da origem do personagem
3. **Classe**: Seleção da classe do agente
4. **Detalhes**: Descrição física, personalidade, histórico
5. **Atributos**: Edição pós-criação (tela separada)

## 🔐 Sistema de Autenticação

- **Registro**: Username, email, senha
- **Login**: Username/email + senha
- **Sessão Persistente**: Token salvo localmente
- **Controle de Acesso**: Personagens públicos/privados
- **Autorização**: Apenas donos podem editar seus personagens

## 🚀 Como Executar

### Backend
```bash
# Instalar dependências
pip install -r app/requirements.txt

# Executar servidor
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
# Instalar dependências
flutter pub get

# Executar aplicação
flutter run
```

## 📱 Funcionalidades do App

### Autenticação
- Login com username/email
- Registro de novos usuários
- Logout automático
- Sessão persistente

### Personagens
- Criação em etapas
- Edição de atributos
- Controle de visibilidade
- Listagem pública/privada

### Interface
- Design responsivo
- Navegação intuitiva
- Feedback visual
- Validação de formulários

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

**SIGIL RPG** - Sistema completo de gerenciamento de personagens de RPG com autenticação e controle de visibilidade.