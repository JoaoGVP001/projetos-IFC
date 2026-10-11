"""Índice exato local, publicação atômica e recuperação híbrida por IDs autorizados."""
from hashlib import sha256
import json
import math
import struct
from uuid import uuid4
from .provedores.ollama import Ollama, validar_config
from .provedores.contratos import Cancelamento

MODELO = 'qwen3-embedding:0.6b'
DIMENSAO = 1024
PERFIL = 'qwen3-retrieval-v1:f32le:l2:1024'
EXTRATOR = 'extracao-v1:trechos-1200-180'
MAX_TRECHOS = 20000
MIN_SIMILARIDADE = .35  # Heurística do piloto, não probabilidade nem garantia de relevância.


def migrar_semantica(db):
    db.execute('''CREATE TABLE semantica_config (id INTEGER PRIMARY KEY CHECK(id=1),
        habilitada INTEGER NOT NULL DEFAULT 0, url TEXT NOT NULL DEFAULT 'http://127.0.0.1:11434',
        modelo TEXT NOT NULL, digest TEXT NOT NULL DEFAULT '', dimensao INTEGER NOT NULL,
        perfil TEXT NOT NULL)''')
    db.execute('INSERT INTO semantica_config(id,modelo,dimensao,perfil) VALUES(1,?,?,?)',(MODELO,DIMENSAO,PERFIL))
    for tabela in ('semantica_vetores','semantica_preparo'):
        db.execute(f'''CREATE TABLE {tabela} (trecho_id INTEGER PRIMARY KEY REFERENCES trechos(id) ON DELETE CASCADE,
            texto_hash TEXT NOT NULL, extrator TEXT NOT NULL, modelo TEXT NOT NULL, digest TEXT NOT NULL,
            dimensao INTEGER NOT NULL, perfil TEXT NOT NULL, vetor BLOB NOT NULL)''')
    db.execute('''CREATE TABLE semantica_trabalho (id INTEGER PRIMARY KEY CHECK(id=1),
        execucao TEXT NOT NULL, estado TEXT NOT NULL, feitos INTEGER NOT NULL DEFAULT 0,
        total INTEGER NOT NULL DEFAULT 0, erro TEXT NOT NULL DEFAULT '',
        atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    db.execute('''CREATE TRIGGER semantica_texto_alterado AFTER UPDATE OF texto ON trechos BEGIN
        DELETE FROM semantica_vetores WHERE trecho_id=new.id;
        DELETE FROM semantica_preparo WHERE trecho_id=new.id; END''')


def assinatura(row):
    return sha256((row['metodo']+'\0'+row['texto']).encode('utf-8')).hexdigest()


def normalizar(vetor):
    if not isinstance(vetor,list) or len(vetor)!=DIMENSAO:
        raise RuntimeError('Dimensão inesperada do embedding; nada foi publicado.')
    if any(type(v) not in (float,int) or not math.isfinite(v) for v in vetor):
        raise RuntimeError('Embedding não finito ou inválido; nada foi publicado.')
    norm=math.sqrt(sum(v*v for v in vetor))
    if not math.isfinite(norm) or norm<1e-12:raise RuntimeError('Embedding vazio ou inválido.')
    return [v/norm for v in vetor]


def decodificar(blob):
    if not isinstance(blob,(bytes,bytearray,memoryview)) or len(blob)!=4*DIMENSAO:raise ValueError('Vetor inválido.')
    values=struct.unpack('<'+str(DIMENSAO)+'f',blob)
    if not all(math.isfinite(v) for v in values) or abs(sum(v*v for v in values)-1)>.002:
        raise ValueError('Normalização inválida.')
    return values


class Embeddings:
    def __init__(self,url):
        self.ollama=Ollama(validar_config({'url':url,'modelo':MODELO,'contexto':2048,'timeout':180}))

    def identidade(self,cancelar=None):
        info=self.ollama.modelo(cancelar,capacidade='embedding')
        if not isinstance(info['digest'],str) or not info['digest']:raise RuntimeError('O modelo local não informou digest.')
        return {'modelo':MODELO,'digest':info['digest'],'dimensao':DIMENSAO,'perfil':PERFIL}

    def gerar(self,textos,consulta=False,cancelar=None):
        if not textos or len(textos)>4 or any(not isinstance(s,str) or not s.strip() or len(s)>6000 for s in textos):
            raise ValueError('Use lotes de até quatro trechos; consultas limitadas a 6.000 caracteres.')
        inputs=['Instruct: Given a study question, retrieve relevant passages that answer the query\nQuery: '+s for s in textos] if consulta else textos
        data=self.ollama.metadados('embed',{'model':MODELO,'input':inputs,'truncate':False,
            'dimensions':DIMENSAO,'keep_alive':0,'options':{'num_gpu':0,'num_thread':4,'num_ctx':2048,'num_batch':32}},
            cancelar,timeout=180 if not consulta else 30)
        if data.get('model')!=MODELO or not isinstance(data.get('embeddings'),list) or len(data['embeddings'])!=len(inputs):
            raise RuntimeError('O runtime retornou embeddings incompatíveis.')
        return [normalizar(v) for v in data['embeddings']]


class IndiceSemantico:
    def __init__(self,h):self.h=h;self.db=h.db

    def config(self):return dict(self.db.execute('SELECT * FROM semantica_config WHERE id=1').fetchone())

    def _trechos(self,ids=None):
        filtro='' if ids is None else ' AND m.id IN (SELECT value FROM json_each(?))'
        return [dict(r) for r in self.db.execute('''SELECT t.*,m.nome,m.tipo,m.url,m.metodo,m.aviso FROM trechos t
            JOIN materiais m ON m.id=t.material_id WHERE m.estado IN ('pronto','parcial')'''+filtro+
            ' ORDER BY t.id LIMIT ?', (MAX_TRECHOS+1,) if ids is None else (json.dumps(ids),MAX_TRECHOS+1))]

    def status(self):
        conf=self.config();job=self.db.execute('SELECT * FROM semantica_trabalho WHERE id=1').fetchone()
        total=self.db.execute("SELECT count(*) FROM trechos t JOIN materiais m ON m.id=t.material_id WHERE m.estado IN ('pronto','parcial')").fetchone()[0]
        # Contagem de cobertura inclui somente o espaço vetorial ativo.
        indexed=self.db.execute('SELECT count(*) FROM semantica_vetores WHERE modelo=? AND digest=? AND dimensao=? AND perfil=?',
            (conf['modelo'],conf['digest'],conf['dimensao'],conf['perfil'])).fetchone()[0]
        return {**conf,'total':total,'indexados':indexed,'pendentes':max(0,total-indexed),
            'trabalho':dict(job) if job else None,'limite':MAX_TRECHOS,'cpu':True}

    def recuperar_interrupcao(self):
        with self.db:self.db.execute("UPDATE semantica_trabalho SET estado='incompleto',erro='Indexação interrompida. Use Indexar / retomar.' WHERE estado='executando'")

    def iniciar(self,url):
        url=validar_config({'url':url})['url']
        token=str(uuid4())
        with self.db:
            self.db.execute('UPDATE semantica_config SET url=? WHERE id=1',(url,))
            self.db.execute("INSERT OR REPLACE INTO semantica_trabalho(id,execucao,estado) VALUES(1,?,'executando')",(token,))
        return token

    def _valido(self,record,row,info):
        return bool(record and record['texto_hash']==assinatura(row) and record['extrator']==EXTRATOR
            and all(record[k]==info[k] for k in ('modelo','digest','dimensao','perfil')))

    def indexar(self,execucao,cancelar=None,progresso=None):
        cancelar=cancelar or Cancelamento()
        config=self.config();client=Embeddings(config['url']);info=client.identidade(cancelar)
        rows=self._trechos()
        if len(rows)>MAX_TRECHOS:raise ValueError('Acervo acima de 20.000 trechos. Reduza o acervo antes de indexar.')
        active={r['trecho_id']:dict(r) for r in self.db.execute('SELECT * FROM semantica_vetores')}
        staged={r['trecho_id']:dict(r) for r in self.db.execute('SELECT * FROM semantica_preparo')}
        pending=[];done=0
        for row in rows:
            record=staged.get(row['id']) or active.get(row['id'])
            if self._valido(record,row,info):
                try:decodificar(record['vetor']);done+=1;continue
                except ValueError:pass
            pending.append(row)
        def progress():
            with self.db:self.db.execute("UPDATE semantica_trabalho SET feitos=?,total=?,atualizado=CURRENT_TIMESTAMP WHERE execucao=?",(done,len(rows),execucao))
            if progresso:progresso(done,len(rows))
        progress()
        for start in range(0,len(pending),4):
            cancelar.verificar();batch=pending[start:start+4]
            vectors=client.gerar([r['texto'] for r in batch],cancelar=cancelar)
            # Troca de pesos durante o trabalho invalida a publicação, mesmo se a tag for a mesma.
            if client.identidade(cancelar)!=info:raise RuntimeError('Os pesos mudaram durante a indexação. Tente reindexar.')
            cancelar.verificar()
            with self.db:
                for row,vector in zip(batch,vectors):
                    now=self.db.execute('SELECT t.*,m.metodo FROM trechos t JOIN materiais m ON m.id=t.material_id WHERE t.id=?',(row['id'],)).fetchone()
                    if now is None or assinatura(now)!=assinatura(row):raise RuntimeError('O material mudou durante a indexação. Retome para atualizar.')
                    self.db.execute('INSERT OR REPLACE INTO semantica_preparo VALUES(?,?,?,?,?,?,?,?)',
                        (row['id'],assinatura(row),EXTRATOR,MODELO,info['digest'],DIMENSAO,PERFIL,struct.pack('<'+str(DIMENSAO)+'f',*vector)))
            done+=len(batch);progress()
        cancelar.verificar()
        if client.identidade(cancelar)!=info:raise RuntimeError('O modelo mudou. Reindexação necessária.')
        # Publica todos os trechos de uma vez; preparação interrompida nunca aparece nas buscas.
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            current=self._trechos()
            if [assinatura(r) for r in current]!=[assinatura(r) for r in rows] or [r['id'] for r in current]!=[r['id'] for r in rows]:
                raise RuntimeError('A biblioteca mudou. Retome a indexação.')
            for row in rows:
                record=self.db.execute('SELECT * FROM semantica_preparo WHERE trecho_id=?',(row['id'],)).fetchone()
                if self._valido(record,row,info):
                    self.db.execute('INSERT OR REPLACE INTO semantica_vetores SELECT * FROM semantica_preparo WHERE trecho_id=?',(row['id'],))
            self.db.execute('DELETE FROM semantica_vetores WHERE digest<>? OR perfil<>? OR modelo<>? OR dimensao<>?',(info['digest'],PERFIL,MODELO,DIMENSAO))
            self.db.execute('DELETE FROM semantica_preparo')
            cancelar.verificar()
            self.db.execute('UPDATE semantica_config SET habilitada=1,modelo=?,digest=?,dimensao=?,perfil=? WHERE id=1',(MODELO,info['digest'],DIMENSAO,PERFIL))
            self.db.execute("UPDATE semantica_trabalho SET estado='concluido',feitos=?,total=?,erro='',atualizado=CURRENT_TIMESTAMP WHERE execucao=?",(done,len(rows),execucao))
        return self.status()

    def candidatos(self,ids,consulta,detalhes=None):
        from .materiais import consulta_fts
        report=detalhes if detalhes is not None else {};conf=self.config()
        report.update(metodo='busca textual',aviso='',escopo='Somente materiais autorizados',indexados=0)
        if not ids:return []
        ids=list(dict.fromkeys(ids));q=consulta_fts(consulta)
        args=json.dumps(ids)
        lexical=[dict(r) for r in self.db.execute('''SELECT t.*,m.nome,m.tipo,m.url,m.metodo,m.aviso FROM trechos_fts
            JOIN trechos t ON t.id=trechos_fts.rowid JOIN materiais m ON m.id=t.material_id
            WHERE trechos_fts MATCH ? AND m.id IN (SELECT value FROM json_each(?))
            AND m.estado IN ('pronto','parcial') ORDER BY bm25(trechos_fts),t.id LIMIT 30''',(q,args))] if q else []
        for row in lexical:row['selecao']='busca textual'
        if not conf['habilitada']:return lexical
        try:
            rows=self._trechos(ids)
            if len(rows)>MAX_TRECHOS:raise RuntimeError('Escopo acima do limite do índice local.')
            records={r['trecho_id']:dict(r) for r in self.db.execute('''SELECT v.* FROM semantica_vetores v JOIN trechos t ON t.id=v.trecho_id
                WHERE t.material_id IN (SELECT value FROM json_each(?))''',(args,))}
            valid=[]
            for row in rows:
                rec=records.get(row['id'])
                if self._valido(rec,row,conf):
                    try:valid.append((row,decodificar(rec['vetor'])))
                    except ValueError:continue
            report['indexados']=len(valid)
            if not valid:raise RuntimeError('Não há vetores válidos neste escopo. Indexe ou retome a biblioteca.')
            client=Embeddings(conf['url'])
            if client.identidade()!= {k:conf[k] for k in ('modelo','digest','dimensao','perfil')}:
                raise RuntimeError('Os pesos/modelo mudaram. Reindexe antes de usar busca semântica.')
            query=client.gerar([consulta],consulta=True)[0]
            if client.identidade()!= {k:conf[k] for k in ('modelo','digest','dimensao','perfil')}:
                raise RuntimeError('Os pesos mudaram durante a busca. Reindexe antes de recuperar por significado.')
            ranked=sorted([(sum(a*b for a,b in zip(query,vec)),row) for row,vec in valid],key=lambda x:(-x[0],x[1]['id']))
            semantic=[(score,row) for score,row in ranked[:30] if score>=MIN_SIMILARIDADE]
            by_id={r['id']:r for r in lexical};scores={r['id']:1/(60+i) for i,r in enumerate(lexical,1)}
            similarities={}
            for i,(score,row) in enumerate(semantic,1):
                by_id[row['id']]=row;scores[row['id']]=scores.get(row['id'],0)+1/(60+i);similarities[row['id']]=score
            result=[];lexical_ids={r['id'] for r in lexical}
            for key in sorted(scores,key=lambda key:(-scores[key],key)):
                row=dict(by_id[key]);row['selecao']='busca híbrida local' if key in similarities and key in lexical_ids else ('busca semântica local' if key in similarities else 'busca textual')
                if key in similarities:row['similaridade']=round(similarities[key],4)
                result.append(row)
            report['metodo']='busca híbrida local'
            if len(valid)<len(rows):report['aviso']='Índice parcial/desatualizado: trechos sem vetor continuam disponíveis pela busca textual. Retome a indexação.'
            return result[:30]
        except (RuntimeError,ValueError,OverflowError) as exc:
            report['aviso']=str(exc)+' Usando busca textual; nenhuma API online foi chamada para buscar.'
            return lexical
