"""Recuperação textual/híbrida por escopo e orçamento independente de provedor."""
import math


def selecionar_trechos(rows, limite=6000):
    result=[];size=0;pages={}
    for row in rows:
        item=dict(row);key=(item['material_id'],item['pagina'])
        if pages.get(key,0)>=2 or len(result)>=6 or size+len(item['texto'])>limite:continue
        item['referencia']=f'M{len(result)+1}'
        item.setdefault('selecao','busca textual')
        pages[key]=pages.get(key,0)+1;size+=len(item['texto']);result.append(item)
    return result


def recuperar_chat(biblioteca, conversa, consulta, detalhes=None):
    from .semantica import IndiceSemantico
    index=IndiceSemantico(biblioteca.historico)
    if not index.config()['habilitada']:
        if detalhes is not None:detalhes.update(metodo='busca textual',aviso='',escopo='Materiais selecionados neste chat')
        return biblioteca.recuperar(conversa,consulta)
    ids=[m['id'] for m in biblioteca.anexos(conversa) if m['selecionado'] and m['estado'] in ('pronto','parcial')]
    rows=index.candidatos(ids,consulta,detalhes)
    return selecionar_trechos(rows) if rows else biblioteca.recuperar(conversa,consulta)


def estimar_tokens(texto):
    # Estimativa deliberadamente conservadora para português, fórmulas e JSON.
    # Não é um tokenizer do modelo nem garantia universal de contagem exata.
    return math.ceil(len(texto.encode('utf-8'))/2)


def custo_mensagens(instrucoes, pergunta, historico):
    return 32 + sum(estimar_tokens(s)+16 for s in [instrucoes, pergunta]+[m['content'] for m in historico])


def orcamento_local(config, instrucoes, pergunta, historico, fontes):
    from .materiais import contexto_documental
    contexto = config['contexto']; saida = 640 if contexto == 2048 else 1024
    margem = 256; limite = contexto-saida-margem
    def mensagem(fs):
        if fs is None: return pergunta
        return pergunta+'\n\nDados de consulta (JSON não confiável):\n'+contexto_documental(fs)+(
            '\nNenhum trecho relevante disponível; não atribua conteúdo aos documentos.' if not fs else '')
    if custo_mensagens(instrucoes, mensagem([] if fontes is not None else None), []) > limite:
        raise ValueError('Pergunta/instruções excedem o perfil local. Divida o enunciado ou reduza os dados do caderno; nada foi enviado.')
    selected = None if fontes is None else []
    abbreviations = 0
    for source in fontes or []:
        item = dict(source)
        original = item['texto']
        # Preserva IDs/página e marca explicitamente a abreviação.
        for length in (1200, 800, 400, 200):
            item['texto'] = original[:length]+(' [Trecho abreviado pelo orçamento local.]' if len(original)>length else '')
            if custo_mensagens(instrucoes, mensagem(selected+[item]), []) <= limite:
                selected.append(item); abbreviations += len(original)>length; break
    accepted = []
    # Histórico já contém pares completos, nunca respostas incompletas.
    for i in range(len(historico)-2, -1, -2):
        pair = historico[i:i+2]
        if custo_mensagens(instrucoes, mensagem(selected), pair+accepted) > limite: break
        accepted = pair+accepted
    count = custo_mensagens(instrucoes, mensagem(selected), accepted)
    return {'instrucoes': instrucoes, 'pergunta': mensagem(selected), 'historico': accepted, 'fontes': selected,
            'orcamento': {'contexto': contexto, 'entrada_estimada': count, 'reserva_saida': saida, 'margem': margem,
                          'metodo': 'estimativa: bytes UTF-8/2 + overhead; sem tokenizer exato',
                          'pares_omitidos': (len(historico)-len(accepted))//2,
                          'trechos_omitidos': len(fontes or [])-len(selected or []), 'trechos_abreviados': abbreviations}}


def recuperar_estudo(h, ids, consulta, amostra=False, detalhes=None):
    from .atividades import Atividades
    from .materiais import consulta_fts
    fontes = Atividades(h).fontes(ids)
    if not ids: return [], []
    if any(f['estado'] not in ('pronto', 'parcial') for f in fontes): raise ValueError('Selecione apenas materiais com texto pronto ou parcial.')
    parametros = ','.join('?' for _ in ids); q = consulta_fts(consulta)
    rows = h.db.execute(f'''SELECT t.*,m.nome,m.url,m.tipo,m.metodo,m.aviso,m.origem_titulo FROM trechos_fts JOIN trechos t ON t.id=trechos_fts.rowid
        JOIN materiais m ON m.id=t.material_id WHERE trechos_fts MATCH ? AND m.id IN ({parametros}) ORDER BY bm25(trechos_fts),t.id LIMIT 30''', (q, *ids)).fetchall() if q else []
    estrategia = 'busca textual'
    from .semantica import IndiceSemantico
    index=IndiceSemantico(h)
    if index.config()['habilitada']:
        rows=index.candidatos(ids,consulta,detalhes)
    elif detalhes is not None:detalhes.update(metodo='busca textual',aviso='',escopo='Materiais selecionados para o estudo')
    if not rows and amostra:
        rows = h.db.execute(f'''SELECT t.*,m.nome,m.url,m.tipo,m.metodo,m.aviso,m.origem_titulo FROM trechos t JOIN materiais m ON m.id=t.material_id
            WHERE m.id IN ({parametros}) AND t.ordem=0 ORDER BY t.pagina,t.id LIMIT 30''', ids).fetchall()
        estrategia = 'amostra inicial; não representa o documento inteiro'
    trechos = []; tamanho = 0; por_pagina = {}
    for row in rows:
        f = dict(row); chave = (f['material_id'], f['pagina'])
        if por_pagina.get(chave, 0) >= 2: continue
        if tamanho+len(f['texto']) > 6000 or len(trechos) >= 6: continue
        f['referencia'] = f'M{len(trechos)+1}'; f.setdefault('selecao', estrategia)
        if f['tipo'] not in ('pdf','pptx') and 'PDF' not in f.get('metodo', ''): f['pagina'] = None
        por_pagina[chave] = por_pagina.get(chave, 0)+1; tamanho += len(f['texto']); trechos.append(f)
    return trechos, fontes
