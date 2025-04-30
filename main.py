from flask import Flask, request
import uuid
import psycopg
import requests

app = Flask(__name__)

connection_db = psycopg.connect(
    dbname="joaoeallam",
    user="postgres",
    password="3f@db",
    host="164.90.152.205",
    port="80"
)

OMDB_API_KEY = "91dc4248"

def create_table():
    with connection_db.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_filmes (
                id UUID PRIMARY KEY,
                imdb_id TEXT UNIQUE,
                titulo TEXT NOT NULL,
                ano INT,
                genero TEXT,
                sinopse TEXT,
                diretor TEXT,
                atores TEXT,
                imagem_url TEXT
            );
        """)
    connection_db.commit()

create_table()

@app.route("/filmes", methods=["GET"])
def buscar_filme():
    titulo = request.args.get("titulo")
    imdb_id = request.args.get("id")

    cursor = connection_db.cursor()
    try:
        if imdb_id:
            cursor.execute("SELECT * FROM cache_filmes WHERE imdb_id = %s", (imdb_id,))
        elif titulo:
            cursor.execute("SELECT * FROM cache_filmes WHERE LOWER(titulo) = LOWER(%s)", (titulo,))
        else:
            return {"erro": "Parâmetro 'titulo' ou 'id' obrigatório"}, 400

        resultado = cursor.fetchone()

        if resultado:
            return {
                "id": resultado[0],
                "imdb_id": resultado[1],
                "titulo": resultado[2],
                "ano": resultado[3],
                "genero": resultado[4],
                "sinopse": resultado[5],
                "diretor": resultado[6],
                "atores": resultado[7],
                "imagem_url": resultado[8]
            }

        # Se não encontrado no banco, buscar na OMDb API
        params = {"apikey": OMDB_API_KEY}
        if imdb_id:
            params["i"] = imdb_id
        else:
            params["t"] = titulo

        resposta = requests.get("https://www.omdbapi.com/", params=params)
        dados = resposta.json()

        if dados.get("Response") == "False":
            return {"erro": "Filme não encontrado na OMDb"}, 404

        # Inserir no banco de dados após buscar na OMDb
        novo_id = uuid.uuid4()
        cursor.execute("""
            INSERT INTO cache_filmes (id, imdb_id, titulo, ano, genero, sinopse, diretor, atores, imagem_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            novo_id,
            dados.get("imdbID"),
            dados.get("Title"),
            int(dados.get("Year", "0").split("–")[0]) if dados.get("Year") else None,
            dados.get("Genre"),
            dados.get("Plot"),
            dados.get("Director"),
            dados.get("Actors"),
            dados.get("Poster")
        ))
        connection_db.commit()

        return {
            "id": novo_id,
            "imdb_id": dados.get("imdbID"),
            "titulo": dados.get("Title"),
            "ano": dados.get("Year"),
            "genero": dados.get("Genre"),
            "sinopse": dados.get("Plot"),
            "diretor": dados.get("Director"),
            "atores": dados.get("Actors"),
            "imagem_url": dados.get("Poster")
        }

    except Exception as e:
        connection_db.rollback()
        return {"erro": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)