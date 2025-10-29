#!/usr/bin/env python3
"""
Teste básico da API Flask
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello World'}

if __name__ == '__main__':
    print("Iniciando API básica...")
    app.run(debug=True, host='0.0.0.0', port=8000)
