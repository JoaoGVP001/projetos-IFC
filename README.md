# 🏛️ Atena

> **Plataforma de estudos gamificada para o ENEM**

Atena é uma aplicação web moderna que transforma o aprendizado em uma experiência gamificada, oferecendo trilhas de conhecimento, campeonatos educacionais e sistema de conquistas para estudantes se prepararem para o ENEM.

![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=for-the-badge&logo=typescript)
![Supabase](https://img.shields.io/badge/Supabase-Latest-green?style=for-the-badge&logo=supabase)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.1.9-38B2AC?style=for-the-badge&logo=tailwind-css)

## ✨ Funcionalidades

### 🎓 Para Estudantes
- **Trilhas de Aprendizado**: Caminhos estruturados por matéria (Matemática, Português, Biologia, etc.)
- **Sistema de XP e Níveis**: Gamificação completa com experiência e progressão
- **Campeonatos**: Competições educacionais entre estudantes
- **Conquistas**: Sistema de badges e achievements
- **Dashboard Personalizado**: Acompanhamento de progresso e estatísticas
- **Ranking**: Leaderboard para motivar a competição saudável

### 👨‍🏫 Para Professores
- **Criação de Turmas**: Gerencie suas turmas com códigos de acesso
- **Banco de Questões**: Crie e gerencie questões personalizadas
- **Campeonatos**: Organize competições para suas turmas
- **Analytics**: Acompanhe o desempenho dos estudantes
- **Gestão de Estudantes**: Visualize e gerencie alunos inscritos

## 🚀 Tecnologias

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS, Radix UI
- **Backend**: Supabase (PostgreSQL, Auth, Real-time)
- **Deployment**: Vercel
- **Package Manager**: pnpm

## 📋 Pré-requisitos

- Node.js 18+ 
- pnpm (recomendado) ou npm
- Conta no Supabase

## ⚠️ Configuração do Banco de Dados

**IMPORTANTE**: Este projeto requer um banco de dados Supabase configurado. O banco atual é apenas para desenvolvimento e não deve ser usado em produção.

### Passos para configurar o banco:

1. **Crie um novo projeto no Supabase**
   - Acesse [supabase.com](https://supabase.com)
   - Crie uma nova conta/projeto
   - Anote a URL e a chave anônima

2. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env.local
   ```
   
   Edite o arquivo `.env.local` com suas credenciais:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=sua_url_do_supabase
   NEXT_PUBLIC_SUPABASE_ANON_KEY=sua_chave_anonima_do_supabase
   ```

3. **Execute os scripts SQL**
   Execute os scripts na ordem correta no SQL Editor do Supabase:
   ```sql
   -- Execute na ordem:
   scripts/001_create_database_schema.sql
   scripts/002_create_profile_trigger.sql
   scripts/003_seed_initial_data.sql
   scripts/004_create_xp_function.sql
   scripts/005_achievement_check_function.sql
   scripts/006_increment_correct_answers.sql
   scripts/007_add_classes_and_subjects.sql
   scripts/008_seed_new_subjects.sql
   scripts/009_fix_question_options_rls.sql
   ```

## 🛠️ Instalação e Desenvolvimento

### 1. Clone o repositório
```bash
git clone https://github.com/JoaoGVP001/atena-next.git
cd atena-next
```

### 2. Instale as dependências
```bash
pnpm install
```

### 3. Configure as variáveis de ambiente
```bash
cp .env.example .env.local
# Edite o .env.local com suas credenciais do Supabase
```

### 4. Execute o banco de dados
Configure o Supabase conforme instruções acima.

### 5. Inicie o servidor de desenvolvimento
```bash
pnpm dev
```

Acesse [http://localhost:3000](http://localhost:3000) no seu navegador.

## 📦 Scripts Disponíveis

```bash
# Desenvolvimento
pnpm dev          # Inicia o servidor de desenvolvimento

# Build e Deploy
pnpm build        # Cria build de produção
pnpm start        # Inicia servidor de produção
pnpm lint         # Executa o linter

# Instalação
pnpm install      # Instala dependências
```

## 🚀 Deploy

### Deploy na Vercel (Recomendado)

1. **Conecte seu repositório à Vercel**
   - Acesse [vercel.com](https://vercel.com)
   - Importe seu repositório GitHub

2. **Configure as variáveis de ambiente**
   - Adicione as variáveis do Supabase no painel da Vercel:
     - `NEXT_PUBLIC_SUPABASE_URL`
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

3. **Deploy automático**
   - A Vercel fará deploy automático a cada push na branch main

### Deploy Manual

```bash
# Build do projeto
pnpm build

# Inicie o servidor de produção
pnpm start
```

## 🏗️ Estrutura do Projeto

```
atena-next/
├── app/                    # App Router do Next.js
│   ├── auth/              # Páginas de autenticação
│   ├── dashboard/         # Dashboard principal
│   ├── learning-paths/    # Trilhas de aprendizado
│   ├── championships/     # Campeonatos
│   ├── teacher/           # Área do professor
│   └── student/           # Área do estudante
├── components/            # Componentes React
│   ├── ui/               # Componentes de UI (Radix)
│   ├── dashboard/        # Componentes do dashboard
│   ├── teacher/          # Componentes do professor
│   └── championships/    # Componentes de campeonatos
├── lib/                  # Utilitários e configurações
│   ├── supabase/         # Cliente Supabase
│   └── types.ts          # Tipos TypeScript
├── scripts/              # Scripts SQL do banco
└── public/               # Arquivos estáticos
```

## 🎯 Funcionalidades Principais

### Sistema de Gamificação
- **XP (Experiência)**: Ganhe pontos respondendo questões
- **Níveis**: Suba de nível conforme acumula XP
- **Streaks**: Mantenha sequências de dias estudando
- **Conquistas**: Desbloqueie badges especiais

### Trilhas de Aprendizado
- **Matérias**: Matemática, Português, Biologia, Física, Química, História, Geografia, Filosofia, Sociologia, Inglês
- **Tópicos**: Conteúdo organizado por dificuldade
- **Progresso**: Acompanhe seu avanço em cada matéria

### Campeonatos
- **Competições**: Participe de campeonatos educacionais
- **Ranking**: Veja sua posição entre outros estudantes
- **Recompensas**: Ganhe XP extra e conquistas

