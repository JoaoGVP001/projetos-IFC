# 🎲 SIGIL RPG - Sistema Completo de Gerenciamento

Sistema completo de gerenciamento de personagens para o sistema de RPG **Sigil**, desenvolvido com **Flutter** (frontend mobile/web) e **Flask** (backend API REST).

![Flutter](https://img.shields.io/badge/Flutter-3.9.2-02569B?logo=flutter)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?logo=flask)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python)

## 📱 Sobre o Projeto

O **SIGIL RPG** é uma aplicação completa para gerenciar personagens do sistema de RPG Sigil, permitindo que jogadores criem, editem e gerenciem seus personagens de forma intuitiva.

## 🏗️ O que cada parte faz

### 🔧 Backend (API Flask) - `SigilRPG_API-main/`

**O que é:** Uma API RESTful desenvolvida em Flask que gerencia todos os dados do sistema.

**O que faz:**
- **Autenticação**: Gerencia login, registro e tokens JWT para segurança
- **Banco de Dados**: Armazena usuários, personagens, campanhas, lutas, habilidades, rituais e itens
- **Lógica de Negócio**: Calcula valores de combate (PV, PE, PS), gerencia relacionamentos entre entidades
- **Endpoints REST**: Fornece URLs para o app Flutter buscar e salvar dados
- **Validação**: Garante que os dados estão corretos antes de salvar

**Tecnologias:** Flask, SQLAlchemy, JWT, SQLite

### 📱 Frontend (App Flutter) - Raiz do projeto

**O que é:** Aplicativo multiplataforma (Android, iOS, Web) que o usuário usa.

**O que faz:**
- **Interface Visual**: Telas bonitas e intuitivas para o usuário interagir
- **Gerenciamento de Personagens**: Criar, editar, visualizar personagens com todos os detalhes
- **Sistema de Combate**: Mostra e permite editar PV/PE/PS durante o jogo
- **Rolador de Dados**: Rola dados com vibração e notificações no celular
- **Campanhas**: Visualizar e gerenciar campanhas de RPG
- **Recursos Mobile**: Vibração e notificações quando rola dados
- **Tema Claro/Escuro**: Interface adaptável

**Tecnologias:** Flutter, Provider (estado), HTTP (comunicação com API)

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
├── scripts/                 # Scripts utilitários
│   ├── tests/              # Scripts de teste da API
│   └── utils/              # Scripts utilitários (servidor, DB)
│
├── docs/                    # Documentação
│   └── COMO_CONFIGURAR_IP_API.md
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

## 🔧 API Flask - Detalhes Técnicos

### O que a API faz

A API Flask é o **cérebro** do sistema. Ela:

1. **Gerencia Usuários**
   - Registra novos usuários
   - Faz login e gera tokens JWT
   - Valida credenciais

2. **Gerencia Personagens**
   - Cria, atualiza, lista e deleta personagens
   - Calcula valores de combate (PV máximo, PE máximo, PS máximo)
   - Armazena atributos, detalhes e histórico

3. **Gerencia Campanhas**
   - Cria e gerencia campanhas de RPG
   - Vincula personagens a campanhas
   - Gerencia equipes (parties)

4. **Gerencia Combates**
   - Registra lutas
   - Calcula experiência ganha
   - Mantém histórico de combates

5. **Gerencia Itens, Habilidades e Rituais**
   - CRUD completo para cada tipo
   - Vincula ao personagem

### Estrutura da API

```
SigilRPG_API-main/
├── app.py                    # Aplicação principal Flask
├── models.py                 # Modelos de banco (User, Character, etc.)
├── routes.py                 # Rotas de autenticação (/api/auth/)
├── user_character_routes.py  # Rotas do personagem do usuário (/api/me/)
├── characters_routes.py      # Rotas de personagens do sistema
├── campaigns_routes.py       # Rotas de campanhas
├── fights_routes.py         # Rotas de combates
├── skills_routes.py         # Rotas de habilidades
├── rituals_routes.py       # Rotas de rituais
├── items_routes.py          # Rotas de itens
└── requirements.txt        # Dependências Python
```

### Endpoints Principais

- **Autenticação**: `/api/auth/login`, `/api/auth/register`
- **Personagens**: `/api/me/` (do usuário), `/api/characters/` (todos)
- **Campanhas**: `/api/v1/campaigns/`
- **Combates**: `/api/me/fights/`

---

## 📱 App Flutter - Detalhes Técnicos

### O que o App faz

O app Flutter é a **interface** que o usuário vê e usa. Ele:

1. **Mostra Telas Bonitas**
   - Interface moderna com Material Design 3
   - Tema claro/escuro
   - Navegação intuitiva

2. **Gerencia Personagens**
   - Cria personagens em wizard de 4 etapas
   - Mostra detalhes completos
   - Permite editar atributos e valores de combate (PV/PE/PS)

3. **Rola Dados**
   - Presets rápidos (d20, 2d6, etc.)
   - Rolagem customizada
   - Vibração e notificação com resultado

4. **Gerencia Campanhas**
   - Lista campanhas
   - Cria e edita campanhas
   - Visualiza detalhes

5. **Comunica com a API**
   - Envia requisições HTTP
   - Recebe e exibe dados
   - Trata erros de conexão

### Estrutura do App

```
lib/
├── main.dart                 # Ponto de entrada
├── constants/               # Cores, rotas, temas
├── controllers/             # Estado (Provider)
├── services/                # Comunicação com API + recursos mobile
├── models/                  # Modelos de dados
├── views/                   # Telas do app
├── widgets/                 # Componentes reutilizáveis
└── utils/                   # Utilitários (dados, combate, API)
```

### Recursos Mobile Especiais

- **Vibração**: Feedback tátil ao rolar dados
- **Notificações**: Mostra resultado dos dados mesmo com app em background
- **Permissões**: Solicita automaticamente ao iniciar o app

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
# Testar se o servidor está rodando
python scripts/tests/test_server.py

# Testar API completa
python scripts/tests/test_api.py

# Testar campanhas
python scripts/tests/test_simple_api.py
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
