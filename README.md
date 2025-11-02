# 🎲 SIGIL RPG - Sistema Completo de Gerenciamento

Sistema completo de gerenciamento de personagens para o sistema de RPG **Sigil**, desenvolvido com **Flutter** (frontend mobile/web) e **Flask** (backend API REST).

![Flutter](https://img.shields.io/badge/Flutter-3.9.2-02569B?logo=flutter)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?logo=flask)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python)

## 📱 Sobre o Projeto

O **SIGIL RPG** é uma aplicação completa para gerenciar personagens do sistema de RPG Sigil, permitindo que jogadores criem, editem e gerenciem seus personagens de forma intuitiva. O sistema inclui:

- ✅ Autenticação de usuários com JWT
- ✅ Criação e gerenciamento de personagens
- ✅ Sistema de campanhas
- ✅ Rolador de dados avançado
- ✅ Sistema de combates
- ✅ **Recursos mobile**: Vibração e notificações push
- ✅ Interface moderna com tema claro/escuro

## 🏗️ Arquitetura do Projeto

O projeto é dividido em duas partes principais:

### Backend (API Flask)
Localizado em `SigilRPG_API-main/`, é uma API RESTful desenvolvida em Flask que fornece todos os dados e operações do sistema.

### Frontend (App Flutter)
Localizado na raiz do projeto, é uma aplicação Flutter multiplataforma (Android, iOS, Web) que consome a API Flask.

```
sigilrpg/
├── SigilRPG_API-main/        # Backend Flask
│   ├── app.py               # Aplicação principal
│   ├── models.py            # Modelos SQLAlchemy
│   ├── routes.py            # Rotas de autenticação
│   ├── characters_routes.py # Rotas de personagens
│   └── requirements.txt     # Dependências Python
│
├── lib/                     # Código Flutter
│   ├── main.dart           # Entry point
│   ├── services/           # Serviços (API, auth, etc.)
│   ├── controllers/        # Gerenciamento de estado
│   ├── views/              # Telas do app
│   └── widgets/            # Componentes reutilizáveis
│
└── pubspec.yaml            # Dependências Flutter
```

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- **Python 3.7+** com pip instalado
- **Flutter SDK** 3.9.2 ou superior
- **Git** (opcional, para clonar o repositório)

### 1️⃣ Backend (API Flask)

#### Passo 1: Navegar para a pasta da API
```bash
cd SigilRPG_API-main
```

#### Passo 2: Criar ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Passo 3: Instalar dependências
```bash
pip install -r requirements.txt
```

#### Passo 4: Configurar variáveis de ambiente (opcional)
```bash
# Copiar arquivo de exemplo
copy env_example.txt .env  # Windows
cp env_example.txt .env    # Linux/Mac

# Editar .env com suas configurações
# (opcional - valores padrão funcionam para desenvolvimento)
```

#### Passo 5: Inicializar banco de dados
```bash
python migrate_db.py
```

#### Passo 6: Popular banco com dados de exemplo (opcional)
```bash
python seed_data.py
```

Este script cria:
- 3 usuários de exemplo (joao@example.com, maria@example.com, pedro@example.com)
- Senha padrão: `123456`
- Personagens e campanhas de exemplo

#### Passo 7: Executar o servidor
```bash
python app.py
```

O servidor estará disponível em:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/
- **Documentação**: http://localhost:8000/docs (se configurado)

---

### 2️⃣ Frontend (App Flutter)

#### Passo 1: Voltar para a raiz do projeto
```bash
cd ..
```

#### Passo 2: Instalar dependências Flutter
```bash
flutter pub get
```

#### Passo 3: Executar o aplicativo

**Para Android/iOS (emulador físico):**
```bash
flutter run
```

**Para Web:**
```bash
flutter run -d chrome
```

**Para Android (específico):**
```bash
flutter run -d android
```

**Para iOS (macOS apenas):**
```bash
flutter run -d ios
```

#### ⚠️ Configuração da URL da API

O app Flutter já está configurado para conectar na API local. A URL é resolvida automaticamente:

- **Web**: `http://localhost:8000`
- **Android Emulator**: `http://10.0.2.2:8000`
- **iOS Simulator**: `http://localhost:8000`
- **Dispositivo físico**: Ajuste `lib/utils/api.dart` com o IP da sua máquina

**Para dispositivo físico Android:**
1. Descubra o IP da sua máquina na rede local
2. Edite `lib/utils/api.dart` e altere a URL para: `http://SEU_IP:8000`

---

## 🔧 Como a API Flask foi Construída

### Estrutura da API

A API Flask segue uma arquitetura modular e organizada:

#### **app.py** - Aplicação Principal
```python
# Configuração base do Flask
- Inicialização do Flask, SQLAlchemy, JWT, CORS
- Registro de blueprints (rotas modulares)
- Configuração de banco de dados (SQLite por padrão)
- Servidor roda na porta 8000
```

#### **models.py** - Modelos de Dados (SQLAlchemy ORM)
```python
# Principais modelos:
- User: Usuários do sistema
- Character: Personagens do jogo
- Fight: Sistema de combates
- Skill: Habilidades dos personagens
- Ritual: Rituais mágicos
- Item: Itens do inventário
```

#### **Rotas Modulares (Blueprints)**

1. **routes.py** (`/api/auth/`)
   - `POST /register` - Registrar novo usuário
   - `POST /login` - Login com username/email + senha
   - `GET /user` - Obter dados do usuário logado
   - `PATCH /` - Atualizar token JWT
   - `DELETE /` - Logout (invalidar token)

2. **characters_routes.py** (`/api/characters/`)
   - `GET /` - Listar todos os personagens
   - `GET /{id}` - Detalhes de um personagem
   - `POST /` - Criar personagem (admin/sistema)
   - `PATCH /{id}` - Atualizar personagem
   - `DELETE /{id}` - Deletar personagem

3. **user_character_routes.py** (`/api/me/`)
   - `POST /` - Criar personagem do usuário logado
   - `GET /` - Obter personagem do usuário
   - `PATCH /` - Atualizar personagem do usuário
   - `DELETE /` - Deletar personagem do usuário

4. **fights_routes.py** (`/api/me/fights/`)
   - `GET /` - Listar lutas do usuário
   - `POST /` - Criar nova luta

5. **skills_routes.py**, **rituals_routes.py**, **items_routes.py**
   - CRUD completo para habilidades, rituais e itens

### Tecnologias Utilizadas na API

- **Flask 2.3.3**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT (tokens de acesso)
- **Flask-CORS**: Suporte para requisições cross-origin
- **Werkzeug**: Hash de senhas seguro (bcrypt)
- **SQLite**: Banco de dados padrão (pode ser trocado por PostgreSQL/MySQL)

### Autenticação JWT

```python
# Como funciona:
1. Usuário faz login → API retorna token JWT
2. Token é enviado em todas as requisições autenticadas:
   Header: Authorization: Bearer <token>
3. Token expira em 24 horas (configurável)
4. Pode ser renovado com endpoint /api/auth/refresh
```

### Banco de Dados

```sql
-- Estrutura principal:
users
  ├── id, name, email, password_hash
  └── created_at, updated_at

characters
  ├── id, name, player_name, age, nex
  ├── agilidade, intelecto, vigor, presenca, forca
  ├── origin, character_class, skilled_in
  ├── gender, appearance, personality, background, objective
  └── user_id (relacionamento com users)

fights
  ├── id, character_id, opponent_id
  ├── status (won/lost/draw)
  └── experience, created_at
```

---

## 📱 Sobre o App Flutter

### Funcionalidades Principais

#### 🎨 **Interface Moderna**
- **Tema claro/escuro** com toggle na AppBar
- **Bottom Navigation Bar** para navegação rápida
- **Dashboard interativo** com estatísticas e ações rápidas
- **Cards visuais** para personagens e campanhas
- **Animações suaves** e transições

#### 👤 **Autenticação**
- Login com username/email + senha
- Registro de novos usuários
- Sessão persistente (token JWT salvo localmente)
- Logout automático

#### 👥 **Personagens**
- **Criação em 4 etapas**:
  1. Dados básicos (nome, idade, etc.)
  2. Origem do personagem
  3. Classe do personagem
  4. Detalhes (aparência, personalidade, histórico)
- **Visualização detalhada** com tabs
- **Edição de atributos** pós-criação
- **Indicadores visuais** de NEX e atributos

#### 🎲 **Rolador de Dados**
- **Presets rápidos** (d20, 2d6, d100, 4d6)
- **Rolagem customizada** (quantidade, lados, modificador)
- **Histórico completo** de rolagens
- **Vibração ao rolar** (recursos mobile)

#### 🏛️ **Campanhas**
- Listagem de campanhas
- Criação e edição
- Status visual (ativa/inativa)
- Informações de jogadores

#### ⚔️ **Combates**
- Sistema de lutas
- Histórico de combates
- Pontos de experiência

### Recursos Mobile

#### 📳 **Vibração**
```dart
// Serviço disponível em lib/services/vibration_service.dart
VibrationService().vibrate();           // Vibração simples
VibrationService().success();          // Vibração de sucesso
VibrationService().error();            // Vibração de erro
VibrationService().mediumImpact();     // Feedback tátil
```

**Onde está sendo usado:**
- Rolagem de dados (`lib/widgets/dice_roller.dart`)

#### 🔔 **Notificações**
```dart
// Serviço disponível em lib/services/notification_service.dart
NotificationService().showNotification(
  id: 1,
  title: 'Sessão Iniciada!',
  body: 'A campanha começa agora!',
);

// Notificação agendada
NotificationService().scheduleNotification(
  id: 2,
  title: 'Lembrete',
  body: 'Sua sessão começa em 1 hora',
  scheduledDate: DateTime.now().add(Duration(hours: 1)),
);
```

**Permissões necessárias:**
- Android: Configurado automaticamente via `AndroidManifest.xml`
- iOS: Requer permissão do usuário (solicitada automaticamente)

### Arquitetura do App Flutter

```
lib/
├── constants/              # Constantes globais
│   ├── app_colors.dart    # Paleta de cores
│   ├── app_routes.dart    # Definição de rotas
│   └── app_theme.dart     # Sistema de temas
│
├── controllers/           # Gerenciamento de estado (Provider)
│   ├── auth_controller.dart
│   ├── characters_controller.dart
│   ├── campaigns_controller.dart
│   └── theme_controller.dart
│
├── services/              # Serviços e comunicação com API
│   ├── auth_service.dart
│   ├── characters_service.dart
│   ├── vibration_service.dart       # ✨ Vibração
│   └── notification_service.dart    # 🔔 Notificações
│
├── models/                # Modelos de dados
│   ├── character.dart
│   ├── campaign.dart
│   └── ...
│
├── views/                 # Telas do aplicativo
│   ├── auth/             # Login e registro
│   ├── home/             # Dashboard
│   ├── characters/       # Gerenciamento de personagens
│   ├── campaigns/        # Gerenciamento de campanhas
│   └── dice/             # Rolador de dados
│
└── widgets/              # Componentes reutilizáveis
    ├── character_card.dart
    ├── custom_button.dart
    └── ...
```

### Tecnologias Utilizadas no App

- **Flutter 3.9.2**: Framework multiplataforma
- **Provider**: Gerenciamento de estado
- **HTTP**: Cliente para comunicação com API
- **Material Design 3**: Design system moderno
- **vibration**: Plugin para vibração
- **flutter_local_notifications**: Notificações locais
- **permission_handler**: Gerenciamento de permissões

---

## 📋 Endpoints Principais da API

### Autenticação
```
POST   /api/auth/register    # Registrar usuário
POST   /api/auth/login       # Login
GET    /api/auth/user        # Usuário atual
```

### Personagens
```
GET    /api/me/              # Personagem do usuário
POST   /api/me/              # Criar personagem
PATCH  /api/me/              # Atualizar personagem
GET    /api/characters       # Listar todos (admin)
GET    /api/characters/{id}  # Detalhes de um personagem
```

### Campanhas
```
GET    /api/campaigns        # Listar campanhas
POST   /api/campaigns        # Criar campanha
PATCH  /api/campaigns/{id}   # Atualizar
DELETE /api/campaigns/{id}   # Deletar
```

### Combates
```
GET    /api/me/fights/       # Lutas do usuário
POST   /api/me/fights/       # Criar luta
```

---

## 🎮 Sistema Sigil RPG

### Atributos do Personagem
- **Agilidade (AGI)**: 0-3
- **Intelecto (INT)**: 0-3
- **Vigor (VIG)**: 0-3
- **Presença (PRE)**: 0-3
- **Força (FOR)**: 0-3

### NEX (Nível de Exposição)
- Valor entre **5 e 99**
- Representa o nível de exposição ao paranormal
- Padrão: **5** (mínimo)

---

## 🔐 Credenciais de Teste

Após executar `python seed_data.py`, você pode usar:

```
Email: joao@example.com
Senha: 123456

Email: maria@example.com
Senha: 123456

Email: pedro@example.com
Senha: 123456
```

---

## 🛠️ Desenvolvimento

### Executar em modo debug
```bash
# Backend
python app.py  # Já roda em modo debug

# Frontend
flutter run  # Hot reload ativado
```

### Testar a API
```bash
cd SigilRPG_API-main
python test_api.py
```

### Estrutura de Banco de Dados
```bash
# Visualizar banco SQLite
sqlite3 instance/rpg.db
# ou usar ferramenta visual como DB Browser for SQLite
```

---

## 📦 Dependências Principais

### Backend (requirements.txt)
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.3
Flask-CORS==4.0.0
Werkzeug==2.3.7
```

### Frontend (pubspec.yaml)
```yaml
flutter: sdk: flutter
http: ^1.2.2
provider: ^6.1.2
vibration: ^1.8.4
flutter_local_notifications: ^17.2.3
permission_handler: ^11.3.1
```

---

## 📝 Notas Importantes

- ✅ O backend deve estar rodando antes de usar o app Flutter
- ✅ Para dispositivos físicos Android, configure o IP da API em `lib/utils/api.dart`
- ✅ Vibração funciona apenas em dispositivos físicos (não em emuladores)
- ✅ Notificações requerem permissões do sistema (solicitadas automaticamente)
- ✅ O banco de dados SQLite é criado automaticamente na primeira execução
- ✅ Tokens JWT expiram em 24 horas (configurável em `app.py`)

---

## 🐛 Solução de Problemas

### API não conecta
- Verifique se o servidor Flask está rodando em `http://localhost:8000`
- Teste acessando `http://localhost:8000/` no navegador
- Para Android físico, use o IP da sua máquina na rede

### Erro de dependências Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de dependências Flutter
```bash
flutter pub get
flutter clean
flutter pub get
```

### Banco de dados não cria
```bash
cd SigilRPG_API-main
python migrate_db.py
```

---

## 📄 Licença

Este projeto é privado e desenvolvido para fins educacionais e pessoais.

---

## 👥 Autor

Desenvolvido para o sistema de RPG **Sigil**.

---

**🎲 SIGIL RPG** - Sistema completo de gerenciamento de personagens com API Flask e aplicativo Flutter multiplataforma.

---

## 📚 Documentação Adicional

- **API Flask**: Veja `SigilRPG_API-main/README.md` para documentação detalhada da API
- **Exemplos de uso**: Veja `lib/services/mobile_features_example.dart` para exemplos de vibração e notificações
- **Estrutura do projeto**: Consulte as seções de arquitetura acima
