# SIGIL RPG – Ordem Paranormal (Flutter + FastAPI)

Aplicativo Flutter para gerenciamento de campanhas e fichas baseado no sistema Ordem Paranormal. O repositório agora inclui um backend FastAPI funcional em `app/` (SQLite por padrão) além do frontend Flutter. Estrutura orientada a MVC no Flutter com foco em uma UI dark, moderna e responsiva.

## ⚙️ Stack
- Flutter (Material 3, tema dark customizado)
- Gerenciamento de estado com Provider (para Dice Roller e expansão futura)
- FastAPI (Python), SQLAlchemy, Pydantic v2
- Banco por padrão: SQLite (arquivo `app.db`).

## 🗂️ Arquitetura (MVC – Flutter)
```
lib/
├── models/           # Entidades e modelos de dados
├── views/            # Telas e fluxos (Home, Characters, Campaigns, Teams, Dice)
├── controllers/      # Lógica de negócio e estado leve
├── widgets/          # Componentes UI reutilizáveis
├── utils/            # Utilitários (ex: dice roller)
└── constants/        # Cores, tema e rotas
```

## ✅ Implementado (Flutter)
- Tema dark custom (cores, tipografia e componentes base)
- Navegação por rotas nomeadas
- Home com atalhos para Personagens, Campanhas, Equipes e Rolador de Dados
- Telas:
  - CharactersListView (lista com mock e navegação)
  - CharacterDetailView (abas: Combate, Habilidades, Rituais, Inventário, Descrição)
  - CharacterCreateView – Wizard (6 etapas): básicas, atributos, origem, classe, perícias/habilidades, equipamento
  - CampaignsView, TeamsView (placeholders)
  - DiceView usando Provider + `DiceRoller` com histórico
- Widgets reutilizáveis: AttributeCircle, SkillRow, CharacterCard, HealthBar, DiceRoller
- Utils: `Dice` (rolagens genéricas e d20)

## 🌐 Backend (Status atual – FastAPI)
- FastAPI com CORS liberado para desenvolvimento
- Banco padrão: SQLite (`app.db` criado automaticamente)
- Lifespan faz setup inicial
- Módulos de rotas em `app/routes`:
  - Root/Health: `/api/v1/health`
  - Characters: `/api/v1/characters/*`
  - Campaigns: `/api/v1/campaigns/*`
  - (Arquivos presentes para `auth`, `users`, `items`, com schemas/services em evolução)

## ▶️ Rodando o projeto
### Backend (FastAPI)
1) Instalar dependências no venv já presente em `app/venv`:
```
cd D:\Desktop\sigilflutter\sigilrpg
app\venv\Scripts\python -m pip install -r app\requirements.txt
```
2) Rodar a API (na raiz do projeto):
```
app\venv\Scripts\python -m uvicorn app.main:app --reload
```
- Docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

Observações:
- Banco de dados padrão é SQLite (`app.db` na raiz). Para usar Postgres, defina `DATABASE_URL` (ex.: `postgresql://user:pass@host:5432/db`).
- No Windows, preferir `python -m uvicorn ...` usando o Python do venv para evitar que o reloader use outro interpretador.

### Frontend (Flutter)
1) Instalar dependências:
```
cd D:\Desktop\sigilflutter\sigilrpg
flutter pub get
```
2) Executar:
```
flutter run
```

### Conectando o Flutter ao Backend
- Base URL por plataforma:
  - Android emulador: `http://10.0.2.2:8000`
  - iOS simulator / Web / Desktop: `http://localhost:8000`
- Dependência sugerida para HTTP no Flutter (`pubspec.yaml`):
```
dependencies:
  http: ^1.2.2
```
- Exemplo: chame `GET /api/v1/health` e exiba o resultado na Home (CORS já liberado no backend).

## 📦 Modelos de dados (parcial – Flutter)
- Character (básico, para lista e detalhe)
- Skill, Item, Ability, Attack, Session, Campaign, Team (com SharedMap/Note)

## 🚧 Em andamento / Próximos passos
- Ficha (Combate): listar perícias com `SkillRow`, ataques equipados e defesas calculadas
- Inventário: CRUD, categorias e cálculo de peso/carga
- Persistência local: Hive/SQLite + repositórios
- Integração de estado: expandir Provider/Riverpod para personagens/campanhas/equipes
- Validações/cálculos: NEX, distribuição de pontos, modificadores, defesas, resistências
- UI/UX: ícones temáticos, animações sutis, responsividade e acessibilidade
- Testes: widget tests para telas e utilitários

---

Projeto com base sólida em Flutter e backend FastAPI integrado. Próximas fases incluem persistência local no app, integração completa de CRUD com a API e colaboração.

### 🛠️ Troubleshooting
- `ImportError: email-validator` (Pydantic v2): já incluído em `app/requirements.txt` (`email-validator`). Reinstale dependências.
- `BaseSettings` movido: usamos `pydantic-settings` (também no `requirements.txt`).
- Uvicorn reloader usando Python errado no Windows: rode com `app\venv\Scripts\python -m uvicorn app.main:app --reload`.
- Postgres opcional (Docker):
```
docker run --name rpg-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=postgres -e POSTGRES_DB=rpg_helper -p 5432:5432 -d postgres:15
```
