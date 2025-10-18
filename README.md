# SIGIL RPG – Ordem Paranormal (Flutter + FastAPI)

Aplicativo Flutter para gerenciamento de campanhas e fichas baseado no sistema Ordem Paranormal. O repositório inclui um backend FastAPI funcional em `app/` (SQLite por padrão) além do frontend Flutter. Estrutura orientada a MVC no Flutter com foco em uma UI dark, moderna e responsiva.

## 🎯 Sistema de Criação de Personagem Implementado

O sistema de criação de personagem está completamente funcional com:

### 📊 **Sistema de Atributos**
- **Distribuição de pontos**: 4 pontos para distribuir entre os 5 atributos
- **Valores iniciais**: Todos começam em 1
- **Limites**: Máximo de 3 por atributo, mínimo de 0 (com bônus de 1 ponto adicional)
- **Interface**: Sliders intuitivos com validação em tempo real

### 🎭 **Sistema de Classes (3 opções)**
- **Combatente**: Focado em combate direto, 20+VIG PV, 2+PRES PE, 12 SAN
- **Especialista**: Versatilidade e conhecimento, 16+VIG PV, 3+PRES PE, 16 SAN  
- **Ocultista**: Poderes paranormais, 12+VIG PV, 4+PRES PE, 20 SAN
- **Interface**: Cards visuais com descrições completas, estatísticas e personagens famosos

### 🌟 **Sistema de Origens (30+ opções)**
- **Origens do Livro "Iniciação"**: Acadêmico, Agente de Saúde, Amnésico, Artista, Atleta, Chef, Investigador, Lutador, Magnata, Mercenário, Militar, Operário, Policial, Religioso, Servidor Público
- **Origens do Suplemento "Sobrevivendo ao Horror"**: Amigo dos Animais, Astronauta, Chef do Outro Lado, Colegial, Cosplayer, Diplomata, Explorador, Experimento, Fanático por Criaturas, Fotógrafo, Inventor Paranormal, Jovem Místico, Legista do Turno da Noite, Mateiro, Mergulhador, Motorista, Nerd Entusiasta, Psicólogo, Profetizado, Repórter Investigativo
- **Cada origem inclui**: Perícias treinadas específicas e poder único
- **Interface**: Cards detalhados com descrições, perícias e poderes

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
- **Tema dark custom** (cores, tipografia e componentes base)
- **Navegação por rotas nomeadas** com MultiProvider configurado
- **Home** com atalhos para Personagens, Campanhas, Equipes e Rolador de Dados
- **Sistema de Criação de Personagem Completo**:
  - **CharacterCreateView** – Wizard (4 etapas): Informações Básicas, Atributos, Classe, Origem
  - **Sistema de Atributos**: Distribuição de 4 pontos com validação em tempo real
  - **Sistema de Classes**: 3 classes com cards visuais, estatísticas e descrições completas
  - **Sistema de Origens**: 30+ origens com perícias treinadas e poderes únicos
- **Telas**:
  - CharactersListView (lista com mock e navegação)
  - CharacterDetailView (abas: Combate, Habilidades, Rituais, Inventário, Descrição)
  - CampaignsView, TeamsView (placeholders)
  - DiceView usando Provider + `DiceRoller` com histórico
- **Widgets reutilizáveis**: AttributeCircle, SkillRow, CharacterCard, HealthBar, DiceRoller
- **Utils**: `Dice` (rolagens genéricas e d20)
- **Modelos de dados**: Character, CharacterClass, CharacterOrigin, CharacterAttributes

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
- **Persistência de personagens**: Salvar personagens criados localmente e na API
- **Ficha completa**: Implementar visualização detalhada com perícias, ataques e defesas
- **Sistema de perícias**: Implementar perícias treinadas baseadas na classe e origem
- **Inventário**: CRUD, categorias e cálculo de peso/carga
- **Integração de estado**: Expandir Provider para gerenciar personagens criados
- **Validações/cálculos**: NEX, modificadores, defesas, resistências baseadas nos atributos
- **UI/UX**: Ícones temáticos, animações sutis, responsividade e acessibilidade
- **Testes**: Widget tests para telas e utilitários

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
