"""Historico SQLite local, separado do repositorio e das chaves."""

import os
import sqlite3
import sys
from pathlib import Path
from uuid import uuid4


def caminho_banco():
    if sys.platform == 'win32':
        raiz = Path(os.getenv('LOCALAPPDATA', Path.home()/'AppData/Local'))
    elif sys.platform == 'darwin':
        raiz = Path.home()/'Library/Application Support'
    else:
        raiz = Path(os.getenv('XDG_DATA_HOME', Path.home()/'.local/share'))
    return raiz/'CadernoMat'/'historico.sqlite3'


class Historico:
    def __init__(self, caminho=None):
        self.caminho = Path(caminho) if caminho else caminho_banco()
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.caminho)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        versao = self.db.execute('PRAGMA user_version').fetchone()[0]
        if versao > 1:
            self.db.close()
            raise RuntimeError('Este historico exige uma versao mais recente do CadernoMat.')
        if versao == 0:
            if self.caminho.stat().st_size:
                with sqlite3.connect(str(self.caminho)+'.backup') as destino:
                    self.db.backup(destino)
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS conversas (id TEXT PRIMARY KEY, titulo TEXT NOT NULL, rascunho TEXT NOT NULL DEFAULT "", atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
                self.db.execute('CREATE TABLE IF NOT EXISTS mensagens (id INTEGER PRIMARY KEY AUTOINCREMENT, conversa_id TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE, papel TEXT NOT NULL, texto TEXT NOT NULL, estado TEXT NOT NULL, provedor TEXT NOT NULL DEFAULT "", modelo TEXT NOT NULL DEFAULT "", criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
                self.db.execute('PRAGMA user_version=1')
        if os.name != 'nt':
            self.caminho.chmod(0o600)

    def criar(self):
        identificador = str(uuid4())
        with self.db:
            self.db.execute('INSERT INTO conversas(id,titulo) VALUES (?,?)',(identificador,'Novo chat'))
        return identificador

    def listar(self):
        return [dict(x) for x in self.db.execute('SELECT * FROM conversas ORDER BY atualizado DESC, rowid DESC')]

    def mensagens(self, conversa):
        return [dict(x) for x in self.db.execute('SELECT * FROM mensagens WHERE conversa_id=? ORDER BY id',(conversa,))]

    def renomear(self, conversa, titulo):
        if not titulo.strip():
            raise ValueError('Digite um titulo.')
        with self.db:
            self.db.execute('UPDATE conversas SET titulo=?, atualizado=CURRENT_TIMESTAMP WHERE id=?',(titulo.strip()[:100],conversa))

    def rascunho(self, conversa, texto):
        with self.db:
            self.db.execute('UPDATE conversas SET rascunho=? WHERE id=?',(texto,conversa))

    def adicionar(self, conversa, papel, texto, estado='ok', provedor='', modelo=''):
        if papel not in {'user','assistant'} or estado not in {'ok','erro'}:
            raise ValueError('Mensagem invalida.')
        with self.db:
            cursor=self.db.execute('INSERT INTO mensagens(conversa_id,papel,texto,estado,provedor,modelo) VALUES (?,?,?,?,?,?)',(conversa,papel,texto,estado,provedor,modelo))
            self.db.execute('UPDATE conversas SET atualizado=CURRENT_TIMESTAMP WHERE id=?',(conversa,))
        return cursor.lastrowid

    def fechar(self):
        self.db.close()
