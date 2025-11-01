# SIGIL RPG - Sistema de Gerenciamento de Personagens

Um sistema completo para criação e gerenciamento de personagens do sistema Sigil RPG, com backend FastAPI e frontend Flutter, incluindo autenticação JWT e controle de personagens por usuário.

## 🎨 Atualizações Recentes (Frontend)

### Phase 1 - Fundação (✅ Implementado)

#### Sistema de Temas Moderno
- ✅ **Tema Claro/Escuro** com toggle na AppBar
- ✅ Suporte para modo sistema (detecta preferência do dispositivo)
- ✅ **ThemeController** para gerenciamento centralizado de temas
- ✅ Gradientes suaves e melhor contraste (WCAG AA)
- ✅ Transições suaves entre temas
- ✅ Cores consistentes em ambos os temas

#### Navegação Moderna
- ✅ **Bottom Navigation Bar** substituindo drawer
- ✅ Ícones animados com feedback visual
- ✅ Quatro seções principais: Início, Personagens, Campanhas, Ferramentas
- ✅ Navegação por PageView com animações
- ✅ **MainScaffold** para gerenciamento unificado de navegação

#### Dashboard Redesenhado (HomeView)
- ✅ Header com gradiente e branding
- ✅ Cards de estatísticas (Personagens, Campanhas) com ícones
- ✅ **Ações Rápidas** com cards visuais modernos
  - Criar Personagem
  - Rolador de Dados
  - Lutas
  - Equipes
- ✅ Seção de atividade recente
- ✅ Pull-to-refresh para atualizar dados
- ✅ Empty state elegante quando não autenticado

#### Cards Aprimorados

**CharacterCard:**
- ✅ Avatar com placeholder elegante e Hero animation
- ✅ Indicador de NEX com barra de progresso visual
- ✅ Badges coloridos para atributos (AGI, INT, VIG, PRE, FOR)
- ✅ Gradiente sutil no background
- ✅ Menu contextual para editar/deletar
- ✅ Animações de hover/press

**CampaignCard:**
- ✅ Gradiente baseado no status (ativa/inativa)
- ✅ Badge visual de status com ícone
- ✅ Ícones para sistema de RPG e jogadores
- ✅ Indicadores visuais melhorados
- ✅ Design mais espaçado e legível

#### Widgets Reutilizáveis
- ✅ **CustomButton** com variantes (primary, secondary, text, icon)
- ✅ **EmptyState** com ilustração e CTA
- ✅ **ErrorState** com retry button
- ✅ **LoadingOverlay** para operações assíncronas
- ✅ **StatCard** para exibir métricas com gradientes

#### Melhorias no Sistema de Dados
- ✅ Presets rápidos (d20, 2d6, d100, 4d6)
- ✅ Display visual do último resultado
- ✅ Histórico melhorado com cards estilizados
- ✅ Confirmação antes de limpar histórico
- ✅ Empty state quando não há rolagens
- ✅ Formatação melhorada dos resultados

#### Estados Consistentes
- ✅ Loading states em todas as views
- ✅ Error handling com retry
- ✅ Empty states padronizados
- ✅ Refresh indicators

### ✅ Atualizações Implementadas (Anteriores)

- Autenticação antes de criar personagens usando `AuthService`
- Personagens do usuário usando `getUserCharacter()`
- Telas de Login e Registro adicionadas e integradas
- UI de Lutas criada e integrada com `FightsService`

## 🚀 Funcionalidades

### Backend (FastAPI)
- **Autenticação JWT**: Sistema completo de login/registro com tokens JWT
- **Gerenciamento de Usuários**: Criação, autenticação e sessões persistentes
- **CRUD de Personagens**: Criação, listagem, atualização e exclusão
- **Controle de Acesso**: Apenas donos podem ver/editar seus personagens
- **API RESTful**: Endpoints organizados com validação de dados
- **Sistema Sigil**: Atributos específicos (Agilidade, Intelecto, Vigor, Presença, Força)
- **Sistema de Campanhas**: CRUD completo para campanhas
- **Sistema de Lutas**: Gerenciamento de combates e histórico

### Frontend (Flutter)
- **Sistema de Temas**: Modo claro/escuro com toggle
- **Navegação Moderna**: Bottom navigation bar
- **Dashboard Interativo**: HomeView com estatísticas e ações rápidas
- **Sistema de Login/Registro**: Interface completa de autenticação
- **Criação de Personagens**: Fluxo multi-etapas (Básico → Origem → Classe → Detalhes)
- **Visualização de Personagens**: Cards modernos com badges e indicadores
- **Edição de Atributos**: Tela dedicada para ajustar atributos pós-criação
- **Rolador de Dados**: Sistema avançado com presets e histórico
- **Gerenciamento de Sessão**: Persistência de login
- **Interface Responsiva**: Design moderno com Material Design 3
- **Estados Consistentes**: Loading, error e empty states padronizados

## 🏗️ Arquitetura

### Backend (Python/FastAPI)
```
SigilRPG_API-main/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações
├── models.py                   # Modelos de dados
├── routes.py                   # Rotas principais
├── characters_routes.py        # Endpoints de personagens
├── fights_routes.py            # Endpoints de lutas
├── user_character_routes.py    # Rotas de personagem do usuário
├── migrate_db.py               # Migrações do banco
├── seed_data.py               # Dados iniciais
└── requirements.txt            # Dependências
```

### Frontend (Flutter)
```
lib/
├── constants/
│   ├── app_colors.dart         # Paleta de cores
│   ├── app_routes.dart         # Definição de rotas
│   └── app_theme.dart          # Sistema de temas (light/dark)
├── controllers/
│   ├── auth_controller.dart    # Controle de autenticação
│   ├── theme_controller.dart   # Controle de temas
│   ├── characters_controller.dart
│   ├── character_draft_controller.dart
│   ├── campaigns_controller.dart
│   ├── teams_controller.dart
│   └── dicecontroller.dart
├── models/
│   ├── character.dart
│   ├── character_class.dart
│   ├── character_origin.dart
│   ├── campaign.dart
│   ├── item.dart
│   └── user.dart
├── services/
│   ├── auth_service.dart
│   ├── characters_service.dart
│   └── campaigns_service.dart
├── utils/
│   ├── api.dart               # Cliente HTTP com autenticação
│   └── dice.dart              # Utilitários de dados
├── views/
│   ├── main_scaffold.dart     # Scaffold principal com bottom nav
│   ├── auth/
│   │   ├── login_view.dart
│   │   └── register_view.dart
│   ├── home/
│   │   └── home_view.dart     # Dashboard redesenhado
│   ├── characters/
│   │   ├── characters_list_view.dart
│   │   ├── character_create_*.dart
│   │   └── character_detail_view.dart
│   ├── campaigns/
│   │   └── campaigns_view.dart
│   ├── dice/
│   │   └── dice_view.dart     # Rolador melhorado
│   └── fights/
│       └── fights_view.dart
└── widgets/
    ├── bottom_nav_bar.dart     # Navegação inferior
    ├── character_card.dart    # Card aprimorado
    ├── campaign_card.dart     # Card aprimorado
    ├── custom_button.dart     # Botão reutilizável
    ├── empty_state.dart       # Estado vazio
    ├── error_state.dart       # Estado de erro
    ├── loading_overlay.dart   # Overlay de loading
    ├── stat_card.dart         # Card de estatística
    ├── dice_roller.dart       # Rolador aprimorado
    └── ... (outros widgets)
```

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validação de dados
- **JWT**: Autenticação com tokens (python-jose)
- **Bcrypt**: Hash de senhas (passlib)
- **Uvicorn**: Servidor ASGI
- **SQLite**: Banco de dados (desenvolvimento)

### Frontend
- **Flutter**: Framework de UI multiplataforma
- **Provider**: Gerenciamento de estado
- **HTTP**: Cliente para APIs
- **Material Design 3**: Design system moderno
- **Hero Animations**: Transições suaves

## 📋 Endpoints da API

### Autenticação (`/api/auth/`)
- `POST /register` - Registrar novo usuário
- `POST /login` - Login de usuário
- `GET /me` - Obter dados do usuário atual
- `POST /refresh` - Renovar token JWT

### Personagens (`/api/characters/` ou `/api/me/`)
- `GET /` - Listar personagens do usuário
- `GET /{id}` - Obter personagem específico
- `POST /` - Criar novo personagem
- `PATCH /{id}` - Atualizar personagem
- `DELETE /{id}` - Excluir personagem

### Campanhas (`/api/campaigns/`)
- `GET /` - Listar campanhas
- `POST /` - Criar campanha
- `PATCH /{id}` - Atualizar campanha
- `DELETE /{id}` - Deletar campanha

### Lutas (`/api/me/fights/`)
- `GET /` - Listar lutas do usuário
- `POST /` - Criar nova luta

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
cd SigilRPG_API-main
pip install -r requirements.txt
```

2. **Inicializar banco de dados**:
```bash
python migrate_db.py
python seed_data.py  # Opcional: dados iniciais
```

3. **Executar servidor**:
```bash
python run_server.py
# ou
python app.py
```

O servidor estará disponível em `http://localhost:8000`
- Documentação Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

3. **Configurar URL da API**:
Edite `lib/utils/api.dart` se necessário para apontar para o servidor correto.

## 📱 Funcionalidades do App

### Interface Principal
- **Bottom Navigation**: Navegação rápida entre seções
- **Toggle de Tema**: Alterna entre modo claro e escuro
- **Dashboard**: Visão geral com estatísticas e ações rápidas

### Autenticação
- Login com username/email
- Registro de novos usuários
- Logout automático
- Sessão persistente com JWT

### Personagens
- Criação em etapas (Básico → Origem → Classe → Detalhes)
- Listagem com cards visuais modernos
- Visualização detalhada com tabs
- Edição de atributos pós-criação
- Indicadores visuais (NEX, atributos)

### Campanhas
- Listagem de campanhas
- Cards com status visual (ativa/inativa)
- Informações de jogadores e sistema

### Ferramentas
- **Rolador de Dados**:
  - Presets rápidos (d20, 2d6, d100, 4d6)
  - Rolagem customizada
  - Histórico completo
  - Display do último resultado

## 🎨 Design System

### Cores
- **Primária**: `#6B46C1` (Roxo místico)
- **Background**: Escuro `#0F0F12` / Claro `#F9FAFB`
- **Surface**: Escuro `#17171B` / Claro `#FFFFFF`
- **Accent**: `#9F7AEA`
- **Estados**: Success `#10B981`, Warning `#F59E0B`, Danger `#EF4444`

### Componentes
- Border radius: 8px, 12px, 16px
- Elevação Material 3
- Espaçamento baseado em 8px (8, 16, 24, 32)
- Transições suaves (300ms)

### Tipografia
- Hierarquia clara (Display, Headline, Title, Body, Label)
- Contraste adequado (WCAG AA)
- System fonts (Material Design 3)

## 🔧 Configuração de Desenvolvimento

### Backend
- **Porta**: 8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Database**: SQLite (`sigilrpg.db`)

### Frontend
- **Web**: http://localhost:8000 (conecta automaticamente)
- **Android Emulator**: http://10.0.2.2:8000
- **iOS Simulator**: http://localhost:8000
- **Hot Reload**: Ativado por padrão

## 📊 Exemplos de Uso

### Registro de Usuário
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
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
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jogador1",
    "password": "senha123"
  }'
```

### Criar Personagem
```bash
curl -X POST "http://localhost:8000/api/characters" \
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

## 🔮 Próximas Funcionalidades (Roadmap)

### Phase 2 - Core Features
- [ ] Wizard de criação de personagem completo com preview em tempo real
- [ ] CharacterDetailView com todas as tabs (Combate, Habilidades, Rituais, Inventário, Descrição)
- [ ] Sistema de dados avançado com vantagem/desvantagem
- [ ] CampaignDetailView completo com dashboard, sessões e ferramentas do mestre
- [ ] Perfil do usuário com configurações

### Phase 3 - Enhancement
- [ ] Sistema de combate melhorado com tracker de iniciativa
- [ ] Ferramentas do mestre avançadas
- [ ] Suporte offline com cache local
- [ ] Animações e transições adicionais
- [ ] Melhorias de acessibilidade

### Phase 4 - Polish
- [ ] Ilustrações e assets customizados
- [ ] Sistema de conquistas/badges
- [ ] Testes automatizados completos
- [ ] Otimizações de performance
- [ ] Funcionalidades avançadas (IA suggestions, etc.)

## 📝 Notas de Desenvolvimento

### Gitignore
- ✅ Configurado para excluir `venv/`, `__pycache__/`, arquivos `.db` e outros arquivos temporários
- ✅ Mantém estrutura limpa no repositório

### Estrutura de Código
- ✅ Separação clara de responsabilidades (controllers, services, views, widgets)
- ✅ Widgets reutilizáveis para consistência
- ✅ Padrões de nomenclatura consistentes
- ✅ Código comentado onde necessário

## 📄 Licença

Este projeto é privado e desenvolvido para fins educacionais e pessoais.

## 👥 Contribuição

Para contribuir com o projeto, entre em contato com os desenvolvedores.

---

**SIGIL RPG** - Sistema completo de gerenciamento de personagens do sistema Sigil RPG com autenticação JWT, interface moderna e design responsivo.

---

## 🎯 Changelog

### v2.0.0 (Atual)
- ✅ Sistema de temas claro/escuro
- ✅ Bottom navigation bar
- ✅ Dashboard redesenhado
- ✅ Cards aprimorados (Personagens e Campanhas)
- ✅ Widgets reutilizáveis
- ✅ Sistema de dados melhorado
- ✅ Estados consistentes (loading, error, empty)
- ✅ Melhorias de UX/UI gerais

### v1.0.0
- Sistema básico de autenticação
- CRUD de personagens
- Interface inicial
