"""Biblioteca persistente e RAG lexical, independentes do provedor de IA."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile
import unicodedata
from uuid import uuid4

from .extracao import Extracao, MAX_ARQUIVO, extrair, tipo_arquivo
from .links import extrair_link, normalizar_url
from .armazenamento import TODOS_CADERNOS

ESTADOS = {'pendente': 'Aguardando', 'processando': 'Processando', 'pronto': 'Pronto',
           'parcial': 'Texto parcial — revise', 'sem_texto': 'Sem texto interpretavel',
           'nao_suportado': 'Formato nao interpretado', 'erro': 'Falha — reprocessar'}


def migrar_materiais(db):
    comandos = [
        '''CREATE TABLE materiais (id TEXT PRIMARY KEY, chave TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL, tipo TEXT NOT NULL, tamanho INTEGER NOT NULL DEFAULT 0,
        caminho TEXT NOT NULL DEFAULT '', url TEXT NOT NULL DEFAULT '',
        estado TEXT NOT NULL DEFAULT 'pendente', aviso TEXT NOT NULL DEFAULT '',
        metodo TEXT NOT NULL DEFAULT '', materia TEXT NOT NULL DEFAULT '',
        assunto TEXT NOT NULL DEFAULT '', etiquetas TEXT NOT NULL DEFAULT '',
        origem_id TEXT REFERENCES conversas(id) ON DELETE SET NULL,
        origem_titulo TEXT NOT NULL, criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE chat_materiais (conversa_id TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
        material_id TEXT NOT NULL REFERENCES materiais(id) ON DELETE CASCADE,
        selecionado INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(conversa_id,material_id))''',
        '''CREATE TABLE paginas (material_id TEXT NOT NULL REFERENCES materiais(id) ON DELETE CASCADE,
        numero INTEGER NOT NULL, texto TEXT NOT NULL, PRIMARY KEY(material_id,numero))''',
        '''CREATE TABLE trechos (id INTEGER PRIMARY KEY, material_id TEXT NOT NULL
        REFERENCES materiais(id) ON DELETE CASCADE, pagina INTEGER NOT NULL,
        ordem INTEGER NOT NULL, texto TEXT NOT NULL)''',
        'CREATE INDEX trechos_material ON trechos(material_id,pagina)',
        '''CREATE VIRTUAL TABLE trechos_fts USING fts5(texto, content='trechos',
        content_rowid='id', tokenize='unicode61 remove_diacritics 2')''',
        '''CREATE TRIGGER trechos_inserir AFTER INSERT ON trechos BEGIN
        INSERT INTO trechos_fts(rowid,texto) VALUES (new.id,new.texto); END''',
        '''CREATE TRIGGER trechos_excluir AFTER DELETE ON trechos BEGIN
        INSERT INTO trechos_fts(trechos_fts,rowid,texto) VALUES ('delete',old.id,old.texto); END''',
        '''CREATE TRIGGER material_origem_titulo AFTER UPDATE OF titulo ON conversas BEGIN
        UPDATE materiais SET origem_titulo=new.titulo WHERE origem_id=new.id; END''',
    ]
    for sql in comandos: db.execute(sql)


def dividir_trechos(texto, tamanho=1200, sobreposicao=180):
    texto = texto.strip()
    inicio = 0
    while inicio < len(texto):
        fim = min(inicio+tamanho, len(texto))
        if fim < len(texto):
            corte = texto.rfind(' ', inicio+tamanho//2, fim)
            if corte > inicio: fim = corte
        yield texto[inicio:fim]
        if fim == len(texto): break
        inicio = fim-sobreposicao


def termos_busca(texto):
    palavras = re.findall(r'\w+', texto.lower(), flags=re.UNICODE)
    comuns = {'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'e', 'um', 'uma',
              'que', 'em', 'no', 'na', 'para', 'por', 'com', 'me', 'eu', 'voce', 'como',
              'qual', 'explique', 'resolva', 'sobre', 'esse', 'essa', 'isso', 'material'}
    return list(dict.fromkeys(p for p in palavras if len(p) > 1 and p not in comuns))[:20]


def consulta_fts(texto):
    return ' OR '.join('"'+p+'"' for p in termos_busca(texto))


def normalizado(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.casefold()) if unicodedata.category(c) != 'Mn')


class Biblioteca:
    def __init__(self, historico, recuperar=False):
        self.historico, self.db = historico, historico.db
        self.raiz = historico.caminho.parent/'materiais'
        self.raiz.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name != 'nt': self.raiz.chmod(0o700)
        self.db.create_function('NORMALIZAR', 1, normalizado)
        if recuperar:
            for guardado in self.raiz.glob('.removido-*'):
                registro = self.db.execute('SELECT id FROM materiais WHERE id=?',(guardado.name.removeprefix('.removido-'),)).fetchone()
                if registro:
                    original = self.caminho_original(registro['id'])
                    if original and not original.exists(): os.replace(guardado,original)
                    else: guardado.unlink(missing_ok=True)
                else: guardado.unlink(missing_ok=True)
            with self.db:
                self.db.execute("UPDATE materiais SET estado='erro', aviso='Processamento interrompido. Use Reprocessar.' WHERE estado IN ('pendente','processando')")

    def obter(self, ident):
        linha = self.db.execute('SELECT * FROM materiais WHERE id=?', (ident,)).fetchone()
        if linha is None: raise ValueError('Material nao encontrado.')
        return dict(linha)

    def caminho_original(self, ident):
        material = self.obter(ident)
        if not material['caminho']: return None
        caminho = (self.raiz/material['caminho']).resolve()
        if caminho.parent != self.raiz.resolve(): raise ValueError('Caminho de material invalido.')
        return caminho

    def vincular(self, ident, conversa, selecionado=None):
        self.obter(ident)
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO chat_materiais(conversa_id,material_id) VALUES (?,?)', (conversa,ident))
            if selecionado is None:
                # Reutilizacao explicita restaura a associacao mesmo quando o anexo ja existe.
                self.db.execute('''INSERT OR IGNORE INTO materiais_cadernos(material_id,caderno_id)
                    SELECT ?,caderno_id FROM conversas WHERE id=? AND caderno_id IS NOT NULL''',(ident,conversa))
            if selecionado is not None:
                self.db.execute('UPDATE chat_materiais SET selecionado=? WHERE conversa_id=? AND material_id=?',
                                (int(selecionado), conversa, ident))

    def desvincular(self, ident, conversa):
        with self.db:
            self.db.execute('DELETE FROM chat_materiais WHERE conversa_id=? AND material_id=?', (conversa,ident))

    def adicionar_arquivo(self, caminho, conversa):
        caminho = Path(caminho)
        info = caminho.stat()
        if not stat.S_ISREG(info.st_mode): raise ValueError('Selecione um arquivo regular.')
        if info.st_size > MAX_ARQUIVO: raise ValueError('Arquivo excede 20 MiB.')
        titulo = self.historico.obter(conversa)['titulo']
        temporario = None
        try:
            with caminho.open('rb') as origem, tempfile.NamedTemporaryFile(dir=self.raiz, delete=False) as destino:
                temporario = Path(destino.name)
                resumo, tamanho = sha256(), 0
                while bloco := origem.read(65536):
                    tamanho += len(bloco)
                    if tamanho > MAX_ARQUIVO: raise ValueError('Arquivo excede 20 MiB.')
                    resumo.update(bloco)
                    destino.write(bloco)
            chave = 'sha256:'+resumo.hexdigest()
            existente = self.db.execute('SELECT id FROM materiais WHERE chave=?', (chave,)).fetchone()
            if existente:
                self.vincular(existente['id'], conversa)
                return existente['id'], False
            # Extensao preservada so para o aplicativo que abre o original; nunca executada aqui.
            ext = caminho.suffix.lower()[:12]
            ext = ext if re.fullmatch(r'\.[a-z0-9]+', ext) else '.bin'
            nome_local = resumo.hexdigest()+ext
            destino = self.raiz/nome_local
            os.replace(temporario, destino)
            ident = str(uuid4())
            try:
                with self.db:
                    self.db.execute('''INSERT INTO materiais(id,chave,nome,tipo,tamanho,caminho,origem_id,origem_titulo)
                                    VALUES (?,?,?,?,?,?,?,?)''',
                                    (ident,chave,caminho.name[:240],tipo_arquivo(caminho.name),tamanho,nome_local,conversa,titulo))
                    self.db.execute('INSERT INTO chat_materiais(conversa_id,material_id) VALUES (?,?)', (conversa,ident))
            except sqlite3.IntegrityError:
                existente = self.db.execute('SELECT id FROM materiais WHERE chave=?',(chave,)).fetchone()
                if existente:
                    self.vincular(existente['id'],conversa)
                    return existente['id'],False
                # Nao apagar um blob que outra instancia possa ter registrado.
                raise
            return ident, True
        finally:
            if temporario: temporario.unlink(missing_ok=True)

    def adicionar_link(self, url, conversa):
        url = normalizar_url(url)
        chave = 'url:'+url
        existente = self.db.execute('SELECT id FROM materiais WHERE chave=?', (chave,)).fetchone()
        if existente:
            self.vincular(existente['id'], conversa)
            return existente['id'], False
        ident = str(uuid4())
        with self.db:
            self.db.execute('''INSERT INTO materiais(id,chave,nome,tipo,url,origem_id,origem_titulo)
                            VALUES (?,?,?,?,?,?,?)''', (ident,chave,url[:240],'link',url,conversa,self.historico.obter(conversa)['titulo']))
            self.db.execute('INSERT INTO chat_materiais(conversa_id,material_id) VALUES (?,?)', (conversa,ident))
        return ident, True

    def processar(self, ident):
        material = self.obter(ident)
        with self.db:
            self.db.execute("UPDATE materiais SET estado='processando', aviso='' WHERE id=?", (ident,))
        if material['tipo'] == 'link':
            resultado, tamanho = extrair_link(material['url'])
        else:
            original = self.caminho_original(ident)
            resultado = extrair(original, original.name)
            tamanho = material['tamanho']
        self.salvar_extracao(ident, resultado, tamanho)

    def salvar_extracao(self, ident, resultado: Extracao, tamanho=None):
        # Extracao e indice sao substituidos atomicamente, inclusive em falhas/reprocessamentos.
        with self.db:
            self.db.execute('DELETE FROM trechos WHERE material_id=?', (ident,))
            self.db.execute('DELETE FROM paginas WHERE material_id=?', (ident,))
            for pagina, texto in resultado.paginas:
                self.db.execute('INSERT INTO paginas VALUES (?,?,?)', (ident,pagina,texto))
                for ordem, trecho in enumerate(dividir_trechos(texto)):
                    self.db.execute('INSERT INTO trechos(material_id,pagina,ordem,texto) VALUES (?,?,?,?)', (ident,pagina,ordem,trecho))
            self.db.execute('UPDATE materiais SET estado=?,aviso=?,metodo=?,tamanho=COALESCE(?,tamanho) WHERE id=?',
                            (resultado.estado,resultado.aviso,resultado.metodo,tamanho,ident))

    def paginas(self, ident):
        return [dict(x) for x in self.db.execute('SELECT numero,texto FROM paginas WHERE material_id=? ORDER BY numero', (ident,))]

    def metadados(self, ident, nome, materia='', assunto='', etiquetas='', cadernos=None):
        if not nome.strip(): raise ValueError('Digite um nome para o material.')
        self.obter(ident)
        ids = self._validar_cadernos(cadernos) if cadernos is not None else None
        with self.db:
            self.db.execute('UPDATE materiais SET nome=?,materia=?,assunto=?,etiquetas=? WHERE id=?',
                            (nome.strip()[:240],materia.strip()[:100],assunto.strip()[:200],etiquetas.strip()[:500],ident))
            if ids is not None:self._substituir_cadernos(ident,ids)

    def materias(self):
        return [x[0] for x in self.db.execute("SELECT DISTINCT materia FROM materiais WHERE materia<>'' ORDER BY materia")]

    def cadernos_material(self, ident):
        return [dict(x) for x in self.db.execute('''SELECT c.* FROM cadernos c JOIN materiais_cadernos m
            ON m.caderno_id=c.id WHERE m.material_id=? ORDER BY c.ordem,c.id''',(ident,))]

    def associar_cadernos(self, ident, cadernos):
        self.obter(ident)
        ids = self._validar_cadernos(cadernos)
        with self.db:self._substituir_cadernos(ident,ids)

    def _validar_cadernos(self,cadernos):
        from .cadernos import Cadernos
        ids = list(dict.fromkeys(cadernos))
        for cid in ids: Cadernos(self.historico).obter(cid)
        return ids

    def _substituir_cadernos(self,ident,ids):
        self.db.execute('DELETE FROM materiais_cadernos WHERE material_id=?',(ident,))
        self.db.executemany('INSERT INTO materiais_cadernos VALUES (?,?)',[(ident,cid) for cid in ids])

    def listar(self, busca='', tipo='', materia='', dias=0, conversa=None, caderno=TODOS_CADERNOS):
        regras, args = [], []
        if caderno is None:
            regras.append('NOT EXISTS (SELECT 1 FROM materiais_cadernos mc WHERE mc.material_id=m.id)')
        elif caderno is not TODOS_CADERNOS:
            regras.append('EXISTS (SELECT 1 FROM materiais_cadernos mc WHERE mc.material_id=m.id AND mc.caderno_id=?)')
            args.append(caderno)
        for campo, valor in [('tipo',tipo),('materia',materia)]:
            if valor:
                regras.append(f'm.{campo}=?'); args.append(valor)
        if dias:
            regras.append('m.criado>=?')
            args.append((datetime.now(timezone.utc)-timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S'))
        if conversa:
            regras.append('EXISTS (SELECT 1 FROM chat_materiais c WHERE c.material_id=m.id AND c.conversa_id=?)')
            args.append(conversa)
        if busca.strip():
            regras.append("(instr(NORMALIZAR(m.nome||' '||m.url||' '||m.materia||' '||m.assunto||' '||m.etiquetas),?)>0 OR EXISTS (SELECT 1 FROM trechos t WHERE t.material_id=m.id AND instr(NORMALIZAR(t.texto),?)>0))")
            args.extend([normalizado(busca.strip())]*2)
        sql = 'SELECT m.* FROM materiais m'+(' WHERE '+' AND '.join(regras) if regras else '')+' ORDER BY m.criado DESC,m.rowid DESC'
        return [dict(x) for x in self.db.execute(sql,args)]

    def anexos(self, conversa):
        return [dict(x) for x in self.db.execute('''SELECT m.*,c.selecionado FROM materiais m JOIN chat_materiais c
        ON c.material_id=m.id WHERE c.conversa_id=? ORDER BY m.criado,m.rowid''', (conversa,))]

    def excluir(self, ident):
        caminho = self.caminho_original(ident)
        guardado = self.raiz/('.removido-'+ident)
        moveu = caminho is not None and caminho.exists()
        if moveu: os.replace(caminho,guardado)
        try:
            with self.db:
                self.db.execute('DELETE FROM materiais WHERE id=?', (ident,))
        except Exception:
            if moveu: os.replace(guardado,caminho)
            raise
        if moveu: guardado.unlink(missing_ok=True)
        # DELETE CASCADE aciona o trigger do FTS, removendo tambem paginas e selecoes.

    def recuperar(self, conversa, pergunta, limite=6000):
        """Contrato de recuperacao: lista de trechos/proveniencia; futuro indice vetorial substituivel."""
        consulta = consulta_fts(pergunta)
        candidatos = [dict(x) for x in self.db.execute('''SELECT t.*,m.nome,m.url,m.tipo,m.metodo,
            bm25(trechos_fts) AS relevancia FROM trechos_fts JOIN trechos t ON t.id=trechos_fts.rowid
            JOIN materiais m ON m.id=t.material_id JOIN chat_materiais c ON c.material_id=m.id
            WHERE trechos_fts MATCH ? AND c.conversa_id=? AND c.selecionado=1
            AND m.estado IN ('pronto','parcial') ORDER BY relevancia,t.id LIMIT 30''', (consulta,conversa))] if consulta else []
        estrategia = 'busca textual'
        pedido_geral = re.search(r'\b(resum\w*|analise|analisar|simulado\w*|prova\w*|atividad\w*|crie|criar)\b', normalizado(pergunta))
        if not candidatos and pedido_geral:
            # Resumos genericos recebem uma amostra inicial identificada, nunca fingem ler tudo.
            candidatos = [dict(x) for x in self.db.execute('''SELECT t.*,m.nome,m.url,m.tipo,m.metodo
                FROM trechos t JOIN materiais m ON m.id=t.material_id
                JOIN chat_materiais c ON c.material_id=m.id WHERE c.conversa_id=? AND c.selecionado=1
                AND m.estado IN ('pronto','parcial') AND t.ordem=0
                ORDER BY t.pagina,m.criado,t.id LIMIT 30''', (conversa,))]
            estrategia = 'amostra inicial; nao representa o documento inteiro'
        fontes, usados, tamanho = [], set(), 0
        # Limita sobreposicao: ate dois trechos por pagina e seis por consulta.
        por_pagina = {}
        for trecho in candidatos:
            chave = (trecho['material_id'],trecho['pagina'])
            if trecho['id'] in usados or por_pagina.get(chave,0) >= 2: continue
            if len(fontes) >= 6 or tamanho + len(trecho['texto']) > limite: break
            usados.add(trecho['id']); por_pagina[chave] = por_pagina.get(chave,0)+1
            trecho['referencia'] = f'M{len(fontes)+1}'
            trecho['selecao'] = estrategia
            fontes.append(trecho); tamanho += len(trecho['texto'])
        return fontes


def contexto_documental(fontes):
    # Serializacao escapa delimitadores e separa metadados do texto nao confiavel.
    return json.dumps([{'referencia': f['referencia'], 'material_id': f.get('material_id'), 'nome': f['nome'], 'url': f['url'],
                        'pagina': f['pagina'] if f['tipo']=='pdf' or 'PDF' in f.get('metodo','') else None,
                        'selecao': f.get('selecao','busca textual'),
                        'texto': f['texto']} for f in fontes], ensure_ascii=False)


def referencias(fontes):
    linhas = []
    for f in fontes:
        pagina = f", pagina {f['pagina']}" if f['tipo'] == 'pdf' or 'PDF' in f.get('metodo','') else ''
        linhas.append(f"- [{f['referencia']}] {f['nome']}{pagina}" + (f" — {f['url']}" if f['url'] else ''))
    return '\n'.join(linhas)
