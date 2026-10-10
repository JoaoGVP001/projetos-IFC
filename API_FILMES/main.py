from flask import Flask, request, jsonify
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
        cursor.execute("DROP TABLE IF EXISTS cache_filmes CASCADE;")
        cursor.execute("""
            CREATE TABLE cache_filmes (
                id UUID PRIMARY KEY,
                imdb_id TEXT UNIQUE,
                titulo TEXT NOT NULL,
                ano TEXT,
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

    try:
        with connection_db.cursor() as cursor:
            if imdb_id:
                cursor.execute("SELECT * FROM cache_filmes WHERE imdb_id = %s", (imdb_id,))
            elif titulo:
                cursor.execute("SELECT * FROM cache_filmes WHERE LOWER(titulo) = LOWER(%s)", (titulo,))
            else:
                # Sem parâmetro, listar todos os filmes do banco local
                cursor.execute("SELECT * FROM cache_filmes")
                resultados = cursor.fetchall()
                return jsonify([
                    {
                        "id": r[0],
                        "imdb_id": r[1],
                        "titulo": r[2],
                        "ano": r[3],
                        "genero": r[4],
                        "sinopse": r[5],
                        "diretor": r[6],
                        "atores": r[7],
                        "imagem_url": r[8]
                    } for r in resultados
                ])

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

        params = {"apikey": OMDB_API_KEY}
        if imdb_id:
            params["i"] = imdb_id
        else:
            params["t"] = titulo

        resposta = requests.get("https://www.omdbapi.com/", params=params)
        dados = resposta.json()

        if dados.get("Response") == "False":
            return {"erro": "Filme não encontrado na OMDb"}, 404

        novo_id = uuid.uuid4()
        with connection_db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cache_filmes (id, imdb_id, titulo, ano, genero, sinopse, diretor, atores, imagem_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novo_id,
                dados.get("imdbID"),
                dados.get("Title"),
                dados.get("Year", "").replace("\u2013", "-").replace("–", "-"),
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
