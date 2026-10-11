"""Historico SQLite local, separado do repositorio e das chaves."""

from contextlib import closing
import os
import sqlite3
import sys
from pathlib import Path
from uuid import uuid4

TODOS_CADERNOS = object()


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
        if versao > 9:
            self.db.close()
            raise RuntimeError('Este historico exige uma versao mais recente do CadernoMat.')
        if versao == 0:
            if self.caminho.stat().st_size:
                with closing(sqlite3.connect(str(self.caminho)+'.backup')) as destino:
                    self.db.backup(destino)
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS conversas (id TEXT PRIMARY KEY, titulo TEXT NOT NULL, rascunho TEXT NOT NULL DEFAULT "", atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
                self.db.execute('CREATE TABLE IF NOT EXISTS mensagens (id INTEGER PRIMARY KEY AUTOINCREMENT, conversa_id TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE, papel TEXT NOT NULL, texto TEXT NOT NULL, estado TEXT NOT NULL, provedor TEXT NOT NULL DEFAULT "", modelo TEXT NOT NULL DEFAULT "", criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
                self.db.execute('PRAGMA user_version=1')
        if versao < 2:
            if versao == 1:
                with closing(sqlite3.connect(str(self.caminho)+'.v1.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt':
                    Path(str(self.caminho)+'.v1.backup').chmod(0o600)
            with self.db:
                self.db.execute('ALTER TABLE conversas ADD COLUMN arquivada INTEGER NOT NULL DEFAULT 0')
                self.db.execute('PRAGMA user_version=2')
        if versao < 3:
            if versao in {1, 2}:
                with closing(sqlite3.connect(str(self.caminho)+'.v2.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt':
                    Path(str(self.caminho)+'.v2.backup').chmod(0o600)
            with self.db:
                self.db.execute('ALTER TABLE conversas ADD COLUMN fixada INTEGER NOT NULL DEFAULT 0')
                self.db.execute('PRAGMA user_version=3')
        if versao < 4:
            if versao in {1, 2, 3}:
                with closing(sqlite3.connect(str(self.caminho)+'.v3.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt':
                    Path(str(self.caminho)+'.v3.backup').chmod(0o600)
            from .materiais import migrar_materiais
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_materiais(self.db)
                    self.db.execute('PRAGMA user_version=4')
            except Exception:
                self.db.close()
                raise
        if versao < 5:
            if versao in {1, 2, 3, 4}:
                with closing(sqlite3.connect(str(self.caminho)+'.v4.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt':
                    Path(str(self.caminho)+'.v4.backup').chmod(0o600)
            from .cadernos import migrar_cadernos
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_cadernos(self.db)
                    self.db.execute('PRAGMA user_version=5')
            except Exception:
                self.db.close()
                raise
        if versao < 6:
            if versao:
                with closing(sqlite3.connect(str(self.caminho)+'.v5.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt': Path(str(self.caminho)+'.v5.backup').chmod(0o600)
            from .atividades import migrar_atividades
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_atividades(self.db)
                    self.db.execute('PRAGMA user_version=6')
            except Exception:
                self.db.close()
                raise
        if versao < 7:
            if versao:
                with closing(sqlite3.connect(str(self.caminho)+'.v6.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt': Path(str(self.caminho)+'.v6.backup').chmod(0o600)
            from .preferencias_ia import migrar_ia
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_ia(self.db)
                    self.db.execute('PRAGMA user_version=7')
            except Exception:
                self.db.close()
                raise
        if versao < 8:
            if versao:
                with closing(sqlite3.connect(str(self.caminho)+'.v7.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt': Path(str(self.caminho)+'.v7.backup').chmod(0o600)
            from .semantica import migrar_semantica
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_semantica(self.db)
                    self.db.execute('PRAGMA user_version=8')
            except Exception:
                self.db.close()
                raise
        if versao < 9:
            if versao:
                with closing(sqlite3.connect(str(self.caminho)+'.v8.backup')) as destino:
                    self.db.backup(destino)
                if os.name != 'nt': Path(str(self.caminho)+'.v8.backup').chmod(0o600)
            from .calculos import migrar_calculos
            try:
                with self.db:
                    self.db.execute('BEGIN')
                    migrar_calculos(self.db)
                    self.db.execute('PRAGMA user_version=9')
            except Exception:
                self.db.close()
                raise
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.create_function('CASEFOLD', 1, lambda texto: texto.casefold())
        if os.name != 'nt':
            self.caminho.chmod(0o600)

    def criar(self, caderno=None):
        from .cadernos import Cadernos
        Cadernos(self).validar_destino(caderno)
        identificador = str(uuid4())
        with self.db:
            self.db.execute('INSERT INTO conversas(id,titulo,caderno_id) VALUES (?,?,?)',(identificador,'Novo chat',caderno))
        return identificador

    def listar(self, busca='', arquivadas=False, caderno=TODOS_CADERNOS):
        # instr faz busca literal, inclusive % e _, sem curingas SQL.
        filtro = '' if caderno is TODOS_CADERNOS else ' AND c.caderno_id IS ?'
        args = (int(arquivadas), busca.strip(), busca.strip().casefold(), busca.strip().casefold())
        if caderno is not TODOS_CADERNOS: args += (caderno,)
        return [dict(x) for x in self.db.execute(
            'SELECT c.* FROM conversas c WHERE c.arquivada=? AND '
            '(?="" OR instr(CASEFOLD(c.titulo),?)>0 OR EXISTS '
            '(SELECT 1 FROM mensagens m WHERE m.conversa_id=c.id AND instr(CASEFOLD(m.texto),?)>0)) '
            +filtro+' ORDER BY c.fixada DESC, c.atualizado DESC, c.rowid DESC', args)]

    def obter(self, conversa):
        registro = self.db.execute('SELECT * FROM conversas WHERE id=?',(conversa,)).fetchone()
        if registro is None:
            raise ValueError('Conversa nao encontrada.')
        return dict(registro)

    def arquivar(self, conversa, arquivada=True):
        with self.db:
            self.db.execute('UPDATE conversas SET arquivada=?, atualizado=CURRENT_TIMESTAMP WHERE id=?',(int(arquivada),conversa))

    def fixar(self, conversa, fixada=True):
        with self.db:
            self.db.execute('UPDATE conversas SET fixada=? WHERE id=?',(int(fixada),conversa))

    def excluir(self, conversa):
        with self.db:
            self.db.execute('DELETE FROM conversas WHERE id=?',(conversa,))

    def mensagens(self, conversa):
        return [dict(x) for x in self.db.execute('''SELECT m.*,q.id AS consulta_id,q.usuario_id AS consulta_usuario_id FROM mensagens m
            LEFT JOIN consultas_ia q ON q.resposta_id=m.id WHERE m.conversa_id=? ORDER BY m.id''',(conversa,))]

    def renomear(self, conversa, titulo):
        if not titulo.strip():
            raise ValueError('Digite um titulo.')
        with self.db:
            self.db.execute('UPDATE conversas SET titulo=?, atualizado=CURRENT_TIMESTAMP WHERE id=?',(titulo.strip()[:100],conversa))

    def rascunho(self, conversa, texto):
        with self.db:
            self.db.execute('UPDATE conversas SET rascunho=? WHERE id=?',(texto,conversa))

    def adicionar(self, conversa, papel, texto, estado='ok', provedor='', modelo=''):
        if papel not in {'user','assistant'} or estado not in {'ok','erro','cancelada','incompleta'}:
            raise ValueError('Mensagem invalida.')
        with self.db:
            cursor=self.db.execute('INSERT INTO mensagens(conversa_id,papel,texto,estado,provedor,modelo) VALUES (?,?,?,?,?,?)',(conversa,papel,texto,estado,provedor,modelo))
            self.db.execute('UPDATE conversas SET atualizado=CURRENT_TIMESTAMP WHERE id=?',(conversa,))
        return cursor.lastrowid

    def fechar(self):
        self.db.close()
