Como iniciar um projeto flask?
- Instale o Python 
- Crie um arquivo python e execute no VS Code
- Instale flask usando pip install Flask
  
- Crie um virtual environment (venv) com os seguintes comando:
python -m venv nomedovenv

- Ativar o Venv
venv\Scripts\activate

- Instale o PsycoPG:
pip install "psycopg[binary]"

- Instale a biblioteca requests:
pip install requests

- Instale a extensão do VS Code chamada REST Client para usar as requisições começarem a funcionar

API de Cache de Filmes e Séries

Esta é uma API REST desenvolvida com Flask e PostgreSQL que disponibiliza informações sobre filmes e séries utilizando o serviço público da [OMDb API](https://www.omdbapi.com/). O objetivo é simular um sistema de cache: os dados buscados são armazenados localmente para acelerar futuras consultas.

Funcionalidades

- Buscar informações de filmes e séries por **título** ou **ID do IMDb**
- Armazenar os dados em um banco de dados local PostgreSQL
- Utilizar o cache local para evitar chamadas desnecessárias à API OMDb
- Retornar todos os filmes e séries já armazenados localmente


Como funciona

1. A API verifica se os dados estão armazenados localmente no PostgreSQL.
2. Se não encontrar, consulta a [OMDb API](https://www.omdbapi.com/).
3. Se a resposta for válida, armazena os dados no banco local e retorna a resposta ao usuário.
