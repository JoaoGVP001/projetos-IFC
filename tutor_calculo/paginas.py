"""Páginas editáveis, versões imutáveis e recursos matemáticos congelados."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import uuid4
from .atividades import identificador,texto
from .cadernos import Cadernos

MAX_SECOES=40
MAX_TEXTO=60000


def migrar_paginas(db):
    db.execute('''CREATE TABLE paginas_estudo(id TEXT PRIMARY KEY,caderno_id TEXT REFERENCES cadernos(id) ON DELETE SET NULL,rascunho TEXT NOT NULL,revisao INTEGER NOT NULL DEFAULT 0,versao INTEGER NOT NULL DEFAULT 0,arquivada INTEGER NOT NULL DEFAULT 0,origens TEXT NOT NULL DEFAULT '[]',referencias TEXT NOT NULL DEFAULT '[]',criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    db.execute('CREATE INDEX paginas_caderno ON paginas_estudo(caderno_id,arquivada,atualizado)')
    db.execute('''CREATE TABLE pagina_versoes(pagina_id TEXT NOT NULL REFERENCES paginas_estudo(id) ON DELETE CASCADE,versao INTEGER NOT NULL,documento TEXT NOT NULL,hash TEXT NOT NULL,criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(pagina_id,versao))''')
    db.execute('''CREATE TABLE pagina_recursos(id TEXT PRIMARY KEY,calculo_id TEXT NOT NULL UNIQUE,resumo TEXT NOT NULL,meta TEXT NOT NULL,imagem TEXT NOT NULL DEFAULT '',hash TEXT NOT NULL DEFAULT '')''')
    db.execute('''CREATE TABLE pagina_jobs(id TEXT PRIMARY KEY,pagina_id TEXT NOT NULL REFERENCES paginas_estudo(id) ON DELETE CASCADE,versao INTEGER NOT NULL,tipo TEXT NOT NULL,estado TEXT NOT NULL,previa TEXT NOT NULL DEFAULT '{}',resultado TEXT,manifesto TEXT,erro TEXT NOT NULL DEFAULT '',criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    db.execute('''CREATE TABLE pagina_materiais(pagina_id TEXT NOT NULL,versao INTEGER NOT NULL,material_id TEXT REFERENCES materiais(id) ON DELETE SET NULL,PRIMARY KEY(pagina_id,versao),FOREIGN KEY(pagina_id,versao) REFERENCES pagina_versoes(pagina_id,versao))''')
    db.execute('''CREATE TABLE pagina_navegacao(id INTEGER PRIMARY KEY CHECK(id=1),pagina_id TEXT REFERENCES paginas_estudo(id) ON DELETE SET NULL)''');db.execute('INSERT INTO pagina_navegacao VALUES(1,NULL)')



def validar(d,recursos=()):
    if not isinstance(d,dict) or set(d)-{'titulo','assunto','fundo','secoes'}:raise ValueError('Conteúdo de página inválido.')
    out={'titulo':texto(d.get('titulo'),180,True),'assunto':texto(d.get('assunto',''),500),'fundo':d.get('fundo','branco'),'secoes':[]}
    if out['fundo'] not in ('branco','pautado','quadriculado'):raise ValueError('Escolha um fundo disponível.')
    ss=d.get('secoes')
    if not isinstance(ss,list) or not 1<=len(ss)<=MAX_SECOES:raise ValueError('Use de uma a quarenta seções.')
    ids=set();length=0
    for raw in ss:
        if not isinstance(raw,dict) or set(raw)-{'id','titulo','texto','origem','recurso'}:raise ValueError('Seção inválida.')
        sid=identificador(raw.get('id'))
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',sid) or sid in ids:raise ValueError('IDs de seção inválidos ou repetidos.')
        ids.add(sid);s={'id':sid,'titulo':texto(raw.get('titulo',''),180),'texto':texto(raw.get('texto',''),15000),'origem':raw.get('origem','usuario')}
        s['texto']=raw.get('texto','') # Preserva recuos e quebras do Markdown após validar tipo/limite.
        if s['origem'] not in ('usuario','ia','ferramenta'):raise ValueError('Origem da seção inválida.')
        rid=raw.get('recurso')
        if rid:
            if rid not in recursos:raise ValueError('Resultado matemático não autorizado nesta página.')
            s['recurso']=rid
            if s['origem']=='ferramenta' and s['texto']:s['origem']='usuario'
        elif s['origem']=='ferramenta':raise ValueError('Um resultado local exige referência a uma ferramenta real.')
        prose=re.sub(r'```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`]*`|\$\$[\s\S]*?\$\$|(?<!\\)\$[^$]*?(?<!\\)\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]', '', s['texto'])
        if re.search(r'</?[a-zA-Z][^>]*>',prose) or re.search(r'!\[.*?\]\s*\(',prose):raise ValueError('Use Markdown sem HTML ou imagens externas. Insira gráficos pelos resultados locais.')
        length+=len(s['texto']);out['secoes'].append(s)
    if len({s['recurso'] for s in out['secoes'] if s.get('recurso')})>6:raise ValueError('Use até seis resultados matemáticos por página.')
    if length>MAX_TEXTO:raise ValueError('Página excede 60000 caracteres. Divida em documentos menores.')
    return out


def nova(titulo='Nova página'):
    return {'titulo':titulo,'assunto':'','fundo':'branco','secoes':[{'id':str(uuid4()),'titulo':'Enunciado','texto':'','origem':'usuario'}]}


class Paginas:
    def __init__(self,h):
        self.h,self.db=h,h.db;self.raiz=h.caminho.parent/'paginas';self.assets=self.raiz/'recursos';self.assets.mkdir(parents=True,exist_ok=True)
        if os.name!='nt':self.raiz.chmod(0o700);self.assets.chmod(0o700)
    def _row(self,pid):
        row=self.db.execute('SELECT * FROM paginas_estudo WHERE id=?',(identificador(pid),)).fetchone()
        if not row:raise ValueError('Página não encontrada.')
        return dict(row)
    def editavel(self,pid):
        row=self._row(pid)
        if row['arquivada']:raise ValueError('Restaure a página para editar.')
        if row['caderno_id']:Cadernos(self.h).validar_destino(row['caderno_id'])
        return row
    def ids_recursos(self,pid):
        r=self._row(pid);ids={s['recurso'] for s in json.loads(r['rascunho'])['secoes'] if s.get('recurso')}
        for v in self.db.execute('SELECT documento FROM pagina_versoes WHERE pagina_id=?',(pid,)):
            ids.update(json.loads(v[0])['recursos'])
        # Referências persistidas da origem também autorizam reinserir um recurso removido do rascunho.
        ids.update(o['recurso'] for o in json.loads(r['origens']) if o.get('recurso'))
        return ids
    def recurso(self,rid,imagem=True):
        row=self.db.execute('SELECT * FROM pagina_recursos WHERE id=?',(identificador(rid),)).fetchone()
        if not row:raise ValueError('Recurso indisponível.')
        r={'id':rid,'resumo':row['resumo'],'rotulo':json.loads(row['meta'])['rotulo']}
        if imagem and row['imagem']:
            import base64
            path=self.assets/row['imagem']
            if path.is_symlink() or not path.is_file() or path.stat().st_size>2_000_000 or sha256(path.read_bytes()).hexdigest()!=row['hash']:raise ValueError('Imagem matemática ausente ou alterada; não será exportada silenciosamente.')
            r['imagem']='data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
        else:r['imagem']=None
        return r
    def render(self,row,content=None,imagem=True):
        content=content or json.loads(row['rascunho']);resources={};warnings=[]
        for s in content['secoes']:
            if not s.get('recurso'):continue
            try:resources[s['recurso']]=self.recurso(s['recurso'],imagem)
            except ValueError as e:
                if not imagem:raise
                resources[s['recurso']]=self.recurso(s['recurso'],False);warnings.append(str(e))
        matter=Cadernos(self.h).obter(row['caderno_id'])['nome'] if row['caderno_id'] else 'Geral'
        for ref in json.loads(row['referencias']):
            if ref.get('material_id') and not self.db.execute('SELECT 1 FROM materiais WHERE id=?',(ref['material_id'],)).fetchone():warnings.append('Material de origem removido: '+ref['nome']+'. A referência e o conteúdo salvo foram preservados.')
        for o in json.loads(row['origens']):
            table={'mensagem':'mensagens','calculo':'calculos','tentativa':'tentativas'}.get(o.get('tipo'))
            if table and not self.db.execute('SELECT 1 FROM '+table+' WHERE id=?',(o['id'],)).fetchone():warnings.append('Origem removida: '+o.get('titulo',o['tipo'])+'. O conteúdo salvo foi preservado.')
        return {'conteudo':content,'materia':matter,'versao':row['versao'] or 'rascunho','recursos':resources,'referencias':json.loads(row['referencias']),'origens':json.loads(row['origens']),'avisos':warnings}
    def obter(self,pid):
        row=self._row(pid);editable=not row['arquivada'] and (not row['caderno_id'] or not Cadernos(self.h).obter(row['caderno_id'])['arquivado'])
        return {**{k:row[k] for k in ('id','caderno_id','revisao','versao','arquivada','criado','atualizado')},'editavel':editable,'rascunho':json.loads(row['rascunho']),'origens':json.loads(row['origens']),'render':self.render(row),'versoes':[dict(v) for v in self.db.execute('SELECT versao,criado FROM pagina_versoes WHERE pagina_id=? ORDER BY versao DESC',(pid,))]}
    def criar(self,caderno,content=None,origens=None,referencias=None):
        Cadernos(self.h).validar_destino(caderno);content=content or nova();pid=str(uuid4())
        allowed={o['recurso'] for o in origens or [] if o.get('recurso')};content=validar(content,allowed)
        with self.db:self.db.execute('INSERT INTO paginas_estudo(id,caderno_id,rascunho,origens,referencias) VALUES(?,?,?,?,?)',(pid,caderno,json.dumps(content,ensure_ascii=False),json.dumps(origens or [],ensure_ascii=False),json.dumps(referencias or [],ensure_ascii=False)))
        return self.obter(pid)
    def rascunho(self,pid,content,revision):
        row=self.editavel(pid)
        if type(revision) is not int or revision!=row['revisao']:raise ValueError('A página mudou. Reabra para evitar sobrescrever outra edição.')
        content=validar(content,self.ids_recursos(pid));encoded=json.dumps(content,ensure_ascii=False)
        if encoded!=row['rascunho']:
            with self.db:self.db.execute('UPDATE paginas_estudo SET rascunho=?,revisao=revisao+1,atualizado=CURRENT_TIMESTAMP WHERE id=?',(encoded,pid))
        return self.obter(pid)
    def salvar(self,pid):
        row=self.editavel(pid);doc=self.render(row,imagem=False);doc['versao']=row['versao']+1
        encoded=json.dumps(doc,ensure_ascii=False,sort_keys=True);hashvalue=sha256(encoded.encode()).hexdigest()
        with self.db:
            self.db.execute('INSERT INTO pagina_versoes(pagina_id,versao,documento,hash) VALUES(?,?,?,?)',(pid,doc['versao'],encoded,hashvalue));self.db.execute('UPDATE paginas_estudo SET versao=?,atualizado=CURRENT_TIMESTAMP WHERE id=?',(doc['versao'],pid))
        return self.obter(pid)
    def versao(self,pid,version):
        self._row(pid)
        if type(version) is not int or version<1:raise ValueError('Escolha uma versão salva.')
        row=self.db.execute('SELECT documento,hash FROM pagina_versoes WHERE pagina_id=? AND versao=?',(pid,version)).fetchone()
        if not row or sha256(row['documento'].encode()).hexdigest()!=row['hash']:raise ValueError('Versão inexistente ou alterada.')
        doc=json.loads(row['documento'])
        for rid in doc['recursos']:doc['recursos'][rid]['imagem']=self.recurso(rid)['imagem']
        return doc
    def listar(self,d):
        bid=d.get('caderno');Cadernos(self.h).obter(bid) if bid else None
        search=texto(d.get('busca',''),300).casefold();archive=d.get('arquivadas',False)
        if type(archive) is not bool:raise ValueError('Filtro inválido.')
        rows=self.db.execute('SELECT id,rascunho,versao,atualizado FROM paginas_estudo WHERE caderno_id IS ? AND arquivada=? ORDER BY atualizado DESC,rowid DESC',(bid,int(archive)))
        items=[]
        for r in rows:
            c=json.loads(r['rascunho'])
            texts=[c['titulo'],c['assunto'],*[s['texto'] for s in c['secoes']],*[self.recurso(s['recurso'],False)['resumo'] for s in c['secoes'] if s.get('recurso')]]
            from .materiais import normalizado
            if search and normalizado(search) not in normalizado(' '.join(texts)):continue
            items.append({'id':r['id'],'titulo':c['titulo'],'assunto':c['assunto'],'versao':r['versao'],'atualizado':r['atualizado']})
        offset=d.get('pagina',0)
        if type(offset) is not int or not 0<=offset<=10000:raise ValueError('Paginação inválida.')
        offset=min(offset,max(0,(len(items)-1)//30));return {'itens':items[offset*30:(offset+1)*30],'total':len(items),'pagina':offset}
    def acao(self,d):
        pid=d.get('id');row=self._row(pid);action=d.get('acao')
        if action=='arquivar':
            if type(d.get('valor')) is not bool:raise ValueError('Estado inválido.')
            if row['caderno_id']:Cadernos(self.h).validar_destino(row['caderno_id'])
            with self.db:self.db.execute('UPDATE paginas_estudo SET arquivada=? WHERE id=?',(int(d['valor']),pid))
        elif action=='duplicar':
            content=deepcopy(json.loads(row['rascunho']));content['titulo']=content['titulo'][:170]+' (cópia)'
            return self.criar(d.get('caderno',row['caderno_id']),content,json.loads(row['origens']),json.loads(row['referencias']))
        elif action=='restaurar_versao':
            doc=self.versao(pid,d.get('versao'));self.rascunho(pid,doc['conteudo'],d.get('revisao'))
        else:raise ValueError('Ação desconhecida. Arquive para preservar versões.')
        return self.obter(pid)
    def importar_calculo(self,app,pid,jid):
        row=self.editavel(pid);exists=self.db.execute('SELECT id FROM pagina_recursos WHERE calculo_id=?',(identificador(jid),)).fetchone()
        record=self.db.execute('SELECT * FROM calculos WHERE id=?',(jid,)).fetchone()
        if not record or record['tipo']!='calculo' or record['estado']!='concluida':raise ValueError('Escolha um resultado local concluído.')
        chat=self.h.obter(record['conversa_id'])
        if chat['caderno_id']!=row['caderno_id']:raise ValueError('Escolha um resultado deste caderno.')
        if exists:rid=exists['id']
        else:
            from .ferramentas_matematicas import resumo as resumo_calculo
            from .discreta import resumo as resumo_discreta
            from .inducao import resumo as resumo_inducao
            result=json.loads(record['resultado']);summary=(resumo_inducao if record['versao']=='inducao-visual-v1' else resumo_discreta if record['versao']=='discreta-v1' else resumo_calculo)(result)
            rid=str(uuid4());name='';hashvalue=''
            if record['artefato']:
                raw=app._calculos.png(jid);hashvalue=sha256(raw).hexdigest();name=hashvalue+'.png';dest=self.assets/name
                if not dest.exists() or dest.is_symlink() or sha256(dest.read_bytes()).hexdigest()!=hashvalue:
                    temp=self.assets/(rid+'.tmp');temp.write_bytes(raw);os.replace(temp,dest)
            meta={'rotulo':('Ilustração · sem verificação matemática · ' if record['versao']=='inducao-visual-v1' else 'Resultado local · ')+record['versao'],'versao':record['versao'],'spec':json.loads(record['spec']),'resultado':result}
            with self.db:self.db.execute('INSERT INTO pagina_recursos VALUES(?,?,?,?,?,?)',(rid,jid,summary,json.dumps(meta,ensure_ascii=False),name,hashvalue))
        content=json.loads(row['rascunho']);content['secoes'].append({'id':str(uuid4()),'titulo':'Resultado matemático','texto':'','origem':'ferramenta','recurso':rid})
        origins=json.loads(row['origens']);origins.append({'tipo':'calculo','id':jid,'recurso':rid,'titulo':'Resultado '+record['versao']})
        content=validar(content,self.ids_recursos(pid)|{rid})
        with self.db:self.db.execute('UPDATE paginas_estudo SET origens=?,rascunho=?,revisao=revisao+1 WHERE id=?',(json.dumps(origins,ensure_ascii=False),json.dumps(content,ensure_ascii=False),pid))
        return self.obter(pid)
