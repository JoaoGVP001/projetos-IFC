from flask import Flask, request
import uuid
import psycopg

app = Flask(__name__)

historico_calculos = []

app = Flask(__name__)
connection_db = psycopg.connect(
    dbname="joaoeallam",
    user="postgres",
    password="3f@db",
    host="164.90.152.205",
    port="80"
)

@app.route("/pessoas", methods=["POST"])
def incluir_pessoa():
    dados_recebidos = request.get_json()
    id = uuid.uuid4()
    nome = dados_recebidos['nome']

    cursor = connection_db.cursor()
    cursor.execute('insert into pessoas (id, nome) values (%s, %s)', (id, nome))
    connection_db.commit()

    return {
        'id': id
    }

@app.route("/pessoas", methods=["GET"])
def get_pessoas():
    cursor = connection_db.cursor()
    cursor.execute('select id, nome from pessoas order by nome')

    lista = []
    for item in cursor:
        lista.append({
            'id': item[0],
            'nome': item[1]
        })
    return lista

@app.route("/pessoas/<id>", methods=["PUT"])
def atualizar_pessoas(id):
    dados_recebidos = request.get_json()
    nome = dados_recebidos['nome']

    cursor = connection_db.cursor()
    cursor.execute('update pessoas set nome = %s where id = %s', (nome, id))
    connection_db.commit()
    return {
        'id': id
    }
@app.route("/soma", methods=["POST"])
def somar():
    dados_recebidos = request.get_json()
    numero1 = dados_recebidos['numero1']
    numero2 = dados_recebidos['numero2']
    resultado = numero1 + numero2

    novo_calculo = {
        "id": str(uuid.uuid4()),
        "numero1": numero1,
        "numero2": numero2,
        "resultado": resultado
    }
    
    historico_calculos.append(novo_calculo)
    return novo_calculo

@app.route("/calculos", methods=["GET"])
def listar_calculos():
    return {"historico": historico_calculos}

@app.route("/deletar/<id>", methods=["DELETE"])
def deletar(id):
    global historico_calculos
    historico_calculos = [calculo for calculo in historico_calculos if calculo['id'] != id]
    
    return {"mensagem": "Cálculo removido com sucesso"}

@app.route("/editar/<id>", methods=["PUT"])
def editar(id):
    dados_recebidos = request.get_json()
    for calculo in historico_calculos:
        if calculo["id"] == id:
            calculo["numero1"] = dados_recebidos.get("numero1", calculo["numero1"])
            calculo["numero2"] = dados_recebidos.get("numero2", calculo["numero2"])
            calculo["resultado"] = calculo["numero1"] + calculo["numero2"]
            return calculo

    return {"erro": "Cálculo não encontrado"}, 404

@app.route("/vendas", methods=["GET"])
def get_vendas():
    cursor = connection_db.cursor()
    cursor.execute('''select * from vendas
left join pessoas on vendas.id_pessoa = pessoas.id
left join produtos on vendas.id_produto = produtos.id''')
    
    lista = []
    for item in cursor:
        lista.append({
            'id': item[0],
            'pessoa': {
                'id': item[1],
                'nome': item[4]
            },
            'produto': {
                'id': item[2],
                'nome': item[6],
                'preco': item[7]
            }
        })

        return lista

if __name__ == "__main__":
    app.run(debug=True)