"""Proveniência documental congelada: envio, conferência e revalidação.

Hashes identificam dados, não a veracidade de uma afirmação ou de uma prova.
Nenhuma consulta é refeita ao abrir uma fonte de uma resposta anterior.
"""
from copy import deepcopy
from hashlib import sha256
import json
import re


def digest(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def identidade(h,mid):
    row=h.db.execute('SELECT chave,estado,metodo,aviso FROM materiais WHERE id=?',(mid,)).fetchone()
    if not row:raise ValueError('Material removido. Confira uma nova prévia.')
    pages=[tuple(r) for r in h.db.execute('SELECT numero,texto FROM paginas WHERE material_id=? ORDER BY numero',(mid,))]
    return {'original':row['chave'],'extracao':digest({'paginas':pages,**dict(row)})}


def congelar(h,fontes):
    if fontes is None:return None
    out=deepcopy(fontes);cache={}
    for f in out:
        mid=f['material_id']
        if mid not in cache:cache[mid]=identidade(h,mid)
        f['proveniencia']={**cache[mid],'versao':1,'trecho_original':digest(f['texto'])}
        f['hash_enviado']=digest(f['texto'])
    return out


def selar_envio(prepared):
    for f in prepared.get('fontes') or []:f['hash_enviado']=digest(f['texto'])
    return prepared


def revalidar(h,b,cid,fontes):
    selected={m['id'] for m in b.anexos(cid) if m['selecionado'] and m['estado'] in ('pronto','parcial')}
    cache={}
    for f in fontes or []:
        mid=f['material_id']
        if mid not in selected:raise ValueError('Material removido, desmarcado ou indisponível. Confira uma nova prévia.')
        p=f.get('proveniencia')
        if not p:continue # Compatibilidade; fontes antigas não ganham hashes retroativamente.
        if mid not in cache:cache[mid]=identidade(h,mid)
        if any(p[k]!=cache[mid][k] for k in ('original','extracao')):
            raise ValueError('Texto extraído ou origem mudou. Confira uma nova prévia; o histórico foi preservado.')
        if f.get('hash_enviado')!=digest(f['texto']):raise ValueError('Trecho da consulta alterado.')


def recuperar(h,mid):
    if type(mid) is not int:raise ValueError('Mensagem inválida.')
    row=h.db.execute('SELECT q.*,m.texto FROM consultas_ia q JOIN mensagens m ON m.id=q.resposta_id WHERE m.id=?',(mid,)).fetchone()
    if not row:raise ValueError('Esta mensagem não tem snapshot documental recuperável.')
    snap=json.loads(row['snapshot']);p=snap.get('preparada') or {}
    exact='fontes' in p
    fonts=deepcopy(p.get('fontes',snap.get('fontes')) or [])
    # O rodapé anexado pelo aplicativo não é evidência de citação do modelo.
    body=re.split(r'\n\n### (?:Fontes citadas nesta resposta|Trechos disponibilizados)',row['texto'],maxsplit=1)[0]
    cited=set(re.findall(r'\[(M\d+)\]',body));cache={}
    for f in fonts:
        prov=f.get('proveniencia');status='legado';warning='Registro antigo sem assinatura de extração; texto do snapshot preservado.'
        current=h.db.execute('SELECT chave FROM materiais WHERE id=?',(f['material_id'],)).fetchone()
        original=bool(current and (not prov or current['chave']==prov['original']))
        if not current:status='removido';warning='Material removido; o trecho utilizado foi preservado.'
        elif prov:
            if f['material_id'] not in cache:cache[f['material_id']]=identidade(h,f['material_id'])
            same=all(prov[k]==cache[f['material_id']][k] for k in ('original','extracao'))
            status='atual' if same else 'alterado';warning='' if same else 'Origem ou extração mudou; este é o trecho histórico, não uma nova busca.'
            if f.get('hash_enviado')!=digest(f['texto']):status='invalido';warning='Snapshot do trecho alterado.';original=False
        f.update(estado_atual=status,aviso_atual=warning,original_disponivel=original,
                 citada=f['referencia'] in cited,unidade='slide' if f['tipo']=='pptx' else 'página',
                 envio_exato=exact,verificacao='Citação/extração não verificam a afirmação matemática.')
    return {'mensagem':mid,'consulta':row['id'],'conversa':row['conversa_id'],
            'estado':row['estado'],
            'pergunta':snap.get('original',snap['pergunta']),'fontes':fonts,'envio_exato':exact,
            'aviso':'Confira se o trecho sustenta a afirmação. Referência existente não significa resposta correta.'}


def fonte(h,mid,ref):
    if not isinstance(ref,str) or not re.fullmatch(r'M[1-6]',ref):raise ValueError('Referência inválida.')
    data=recuperar(h,mid)
    f=next((f for f in data['fontes'] if f['referencia']==ref),None)
    if not f:raise ValueError('Referência não enviada nesta consulta.')
    return f


def origem_ferramenta(h,cid,mid):
    if mid is None:return {}
    data=recuperar(h,mid)
    if data['conversa']!=cid:raise ValueError('Escolha uma resposta deste chat.')
    return {'origem_estudo':{'mensagem':mid,'consulta':data['consulta'],
            'fontes':data['fontes'],'aviso':'Operação escolhida pelo usuário; não certifica a resposta inteira.'}}
