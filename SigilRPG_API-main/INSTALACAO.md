# Instruções de Instalação e Execução

## Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. **Clone ou baixe o projeto**
   ```bash
   # Se você tem o projeto em uma pasta
   cd REST-API-for-basic-RPG-flask
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # No Windows:
   venv\Scripts\activate
   
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   # Copie o arquivo de exemplo
   copy env_example.txt .env
   
   # Edite o arquivo .env com suas configurações
   # (opcional, os valores padrão funcionam para desenvolvimento)
   ```

## Execução

1. **Execute o script de dados iniciais**
   ```bash
   python seed_data.py
   ```
   Isso criará usuários, personagens e lutas de exemplo.

2. **Inicie o servidor**
   ```bash
   python app.py
   ```

3. **A API estará disponível em:**
   ```
   http://localhost:8000
   ```

## Testando a API

1. **Execute o script de teste**
   ```bash
   python test_api.py
   ```

2. **Ou teste manualmente com curl/Postman**

   **Login:**
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"email":"joao@example.com","password":"123456"}' \
     http://localhost:8000/api/auth/login
   ```

   **Listar personagens:**
   ```bash
   curl http://localhost:8000/api/characters
   ```

## Estrutura do Projeto

```
REST-API-for-basic-RPG-flask/
├── app.py                    # Aplicação principal
├── models.py                 # Modelos de dados
├── routes.py                 # Rotas de autenticação
├── characters_routes.py       # Rotas de personagens
├── user_character_routes.py  # Rotas do personagem do usuário
├── fights_routes.py          # Rotas de lutas
├── config.py                 # Configurações
├── seed_data.py              # Script de dados iniciais
├── test_api.py               # Script de teste
├── requirements.txt           # Dependências
├── env_example.txt           # Exemplo de configuração
└── README.md                 # Documentação
```

## Endpoints Disponíveis

### Autenticação
- `POST /api/auth/login` - Login
- `GET /api/auth/user` - Usuário autenticado
- `PATCH /api/auth/` - Atualizar token
- `DELETE /api/auth/` - Invalidar token

### Personagens
- `GET /api/characters` - Listar todos os personagens
- `GET /api/characters/{id}` - Detalhes de um personagem

### Personagem do Usuário
- `POST /api/me/` - Criar personagem do usuário
- `GET /api/me/` - Ver personagem do usuário

### Lutas
- `GET /api/me/fights/` - Listar lutas do usuário
- `POST /api/me/fights/` - Criar nova luta

## Dados de Exemplo

O script `seed_data.py` cria:

**Usuários:**
- joao@example.com / 123456
- maria@example.com / 123456
- pedro@example.com / 123456

**Personagens:**
- Aragorn (usuário: joao@example.com)
- Legolas (usuário: maria@example.com)
- Gandalf, Gimli, Frodo (sem usuário - NPCs)

## Solução de Problemas

1. **Erro de importação circular:**
   - Certifique-se de que está executando `python app.py` da pasta correta

2. **Erro de banco de dados:**
   - Execute `python seed_data.py` primeiro para criar as tabelas

3. **Erro de dependências:**
   - Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`

4. **Porta já em uso:**
   - Altere a porta no arquivo `app.py` se necessário


