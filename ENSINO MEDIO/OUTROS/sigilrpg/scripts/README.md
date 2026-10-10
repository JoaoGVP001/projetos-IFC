# 📜 Scripts

Esta pasta contém scripts utilitários e de teste do projeto.

## 📁 Estrutura

```
scripts/
├── tests/          # Scripts de teste da API
└── utils/          # Scripts utilitários
```

## 🧪 Tests (`tests/`)

Scripts para testar a API Flask:

- **`test_server.py`** - Verifica se o servidor está rodando (health check)
- **`test_api.py`** - Testes completos da API (registro, login, etc)
- **`test_simple_api.py`** - Testes específicos de campanhas

### Como usar:

```bash
# Testar se o servidor está rodando
python scripts/tests/test_server.py

# Testar API completa
python scripts/tests/test_api.py

# Testar campanhas
python scripts/tests/test_simple_api.py
```

## 🛠️ Utils (`utils/`)

Scripts utilitários para desenvolvimento:

- **`run_server.py`** - Inicia o servidor Flask de desenvolvimento
- **`create_db.py`** - Cria as tabelas do banco de dados

### Como usar:

```bash
# Iniciar servidor
python scripts/utils/run_server.py

# Criar banco de dados
python scripts/utils/create_db.py
```

## ⚠️ Nota

Certifique-se de que a API está configurada corretamente em `SigilRPG_API-main/` antes de executar os scripts.

