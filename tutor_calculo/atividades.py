"""Atividades versionadas; validação independente de interface e de provedores."""
import json
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from .cadernos import Cadernos

FORMATOS = ('aberta', 'escolha', 'vf', 'numerica')
DIFICULDADES = ('basica', 'intermediaria', 'avancada')


def texto(v, limite=8000, obrigatorio=False):
    if not isinstance(v, str) or len(v) > limite or '\x00' in v:
        raise ValueError(f'Texto inválido: limite de {limite} caracteres.')
    if obrigatorio and not v.strip(): raise ValueError('Preencha o campo obrigatório.')
    return v.strip()


def identificador(v):
    return texto(v, 100, True)


def numero(v):
    if isinstance(v, bool) or not isinstance(v, (str, int, float)):
        raise ValueError('Informe um número decimal finito, sem expressões.')
    try: n = Decimal(str(v).strip().replace(',', '.'))
    except InvalidOperation as exc: raise ValueError('Número inválido. Use decimal ou notação científica.') from exc
    if not n.is_finite() or abs(n) > Decimal('1e100') or (n and abs(n) < Decimal('1e-100')):
        raise ValueError('Número fora do limite: de 1e-100 a 1e100 em módulo, ou zero.')
    return n


def validar_conteudo(d, fontes=None):
    if not isinstance(d, dict): raise ValueError('Atividade inválida.')
    out = {k: texto(d.get(k, ''), lim, k == 'titulo') for k, lim in
           [('titulo', 180), ('descricao', 3000), ('assuntos', 500), ('etiquetas', 500), ('objetivo', 1500)]}
    out['dificuldade'] = d.get('dificuldade', 'basica')
    if out['dificuldade'] not in DIFICULDADES: raise ValueError('Dificuldade inválida.')
    qs = d.get('exercicios')
    if not isinstance(qs, list) or not 1 <= len(qs) <= 30: raise ValueError('Use de 1 a 30 exercícios por atividade.')
    out['exercicios'] = []; ids = set()
    for raw in qs:
        if not isinstance(raw, dict): raise ValueError('Exercício inválido.')
        q = {k: texto(raw.get(k, ''), lim, k == 'enunciado') for k, lim in
             [('enunciado', 8000), ('assunto', 500), ('explicacao', 8000)]}
        q['id'] = identificador(raw.get('id') or str(uuid4()))
        if q['id'] in ids: raise ValueError('IDs de exercícios repetidos.')
        ids.add(q['id']); q['formato'] = raw.get('formato'); q['dificuldade'] = raw.get('dificuldade', out['dificuldade'])
        if q['formato'] not in FORMATOS: raise ValueError('Formato de exercício desconhecido.')
        if q['dificuldade'] not in DIFICULDADES: raise ValueError('Dificuldade do exercício inválida.')
        q['alternativas'] = []; resposta = raw.get('resposta', '')
        if q['formato'] == 'escolha':
            alts = raw.get('alternativas')
            if not isinstance(alts, list) or not 2 <= len(alts) <= 6: raise ValueError('Use de 2 a 6 alternativas.')
            vistos, nomes = set(), set()
            for a in alts:
                if not isinstance(a, dict): raise ValueError('Alternativa inválida.')
                aid = identificador(a.get('id') or str(uuid4())); t = texto(a.get('texto'), 2000, True)
                chave = ' '.join(t.casefold().split())
                if aid in vistos or chave in nomes: raise ValueError('Alternativas vazias ou repetidas.')
                vistos.add(aid); nomes.add(chave); q['alternativas'].append({'id': aid, 'texto': t})
            if not isinstance(resposta, str) or resposta not in vistos: raise ValueError('Escolha uma alternativa correta existente.')
        elif q['formato'] == 'vf':
            if type(resposta) is not bool: raise ValueError('Informe verdadeiro ou falso no gabarito.')
        elif q['formato'] == 'numerica':
            resposta = str(numero(resposta)); tol = numero(raw.get('tolerancia', '0'))
            if tol < 0: raise ValueError('Tolerância absoluta deve ser zero ou positiva.')
            q['tolerancia'] = str(tol)
        else: resposta = texto(resposta, 8000)
        q['resposta'] = resposta
        refs = raw.get('referencias', [])
        if not isinstance(refs, list) or len(refs) > 10: raise ValueError('Referências inválidas.')
        q['referencias'] = []
        for ref in refs:
            if not isinstance(ref, dict): raise ValueError('Referência inválida.')
            mid = identificador(ref.get('material_id')); pagina = ref.get('pagina')
            if pagina is not None and (type(pagina) is not int or not 1 <= pagina <= 100000): raise ValueError('Página inválida.')
            if fontes is not None and not any(f['material_id'] == mid and (pagina is None or f['pagina'] == pagina) for f in fontes):
                raise ValueError('A IA citou uma fonte/página que não foi disponibilizada. Revise a proposta.')
            q['referencias'].append({'material_id': mid, 'pagina': pagina})
        out['exercicios'].append(q)
    return out


def migrar_atividades(db):
    for sql in [
        '''CREATE TABLE atividades(id TEXT PRIMARY KEY, caderno_id TEXT REFERENCES cadernos(id) ON DELETE SET NULL,
        origem_chat TEXT REFERENCES conversas(id) ON DELETE SET NULL, origem_titulo TEXT NOT NULL DEFAULT '',
        origem TEXT NOT NULL CHECK(origem IN ('manual','ia')), fontes TEXT NOT NULL, proveniencia TEXT NOT NULL,
        versao INTEGER NOT NULL, conteudo TEXT NOT NULL, arquivada INTEGER NOT NULL DEFAULT 0,
        criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE atividade_versoes(atividade_id TEXT REFERENCES atividades(id) ON DELETE RESTRICT,
        versao INTEGER NOT NULL, conteudo TEXT NOT NULL, criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(atividade_id,versao))''',
        '''CREATE TABLE tentativas(id TEXT PRIMARY KEY, atividade_id TEXT NOT NULL, versao INTEGER NOT NULL,
        snapshot TEXT NOT NULL, respostas TEXT NOT NULL DEFAULT '{}', posicao INTEGER NOT NULL DEFAULT 0,
        estado TEXT NOT NULL DEFAULT 'andamento' CHECK(estado IN ('andamento','finalizada')),
        inicio TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, fim TEXT, resultado TEXT NOT NULL DEFAULT '{}',
        FOREIGN KEY(atividade_id,versao) REFERENCES atividade_versoes(atividade_id,versao) ON DELETE RESTRICT)''',
        'CREATE INDEX atividades_caderno ON atividades(caderno_id,arquivada)',
        'CREATE INDEX tentativas_atividade ON tentativas(atividade_id,inicio)',
        '''CREATE TABLE atividade_jobs(id TEXT PRIMARY KEY, tipo TEXT NOT NULL, estado TEXT NOT NULL,
        previa TEXT NOT NULL, alvo TEXT NOT NULL DEFAULT '', exercicio TEXT NOT NULL DEFAULT '',
        resultado TEXT, erro TEXT NOT NULL DEFAULT '', criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE estudo_navegacao(id INTEGER PRIMARY KEY CHECK(id=1), area TEXT NOT NULL DEFAULT 'chat',
        atividade TEXT REFERENCES atividades(id) ON DELETE SET NULL,
        tentativa TEXT REFERENCES tentativas(id) ON DELETE SET NULL)''',
        'INSERT INTO estudo_navegacao(id) VALUES(1)',
    ]: db.execute(sql)


class Atividades:
    def __init__(self, h): self.h, self.db = h, h.db

    def obter(self, aid):
        row = self.db.execute('SELECT * FROM atividades WHERE id=?', (identificador(aid),)).fetchone()
        if not row: raise ValueError('Atividade não encontrada.')
        a = dict(row)
        for k in ['conteudo', 'fontes', 'proveniencia']: a[k] = json.loads(a[k])
        a['caderno_arquivado'] = bool(a['caderno_id'] and Cadernos(self.h).obter(a['caderno_id'])['arquivado'])
        a['fontes'] = [{**f, 'disponivel': bool(self.db.execute('SELECT 1 FROM materiais WHERE id=?', (f['id'],)).fetchone())} for f in a['fontes']]
        a['origem_disponivel'] = bool(a['origem_chat'])
        return a

    def editavel(self, aid):
        a = self.obter(aid)
        if a['arquivada'] or a['caderno_arquivado']: raise ValueError('Restaure a atividade e o caderno para continuar trabalhando.')
        return a

    def fontes(self, ids):
        if not isinstance(ids, list) or len(ids) > 10 or len(set(identificador(i) for i in ids)) != len(ids):
            raise ValueError('Escolha até 10 materiais distintos.')
        resultado = []
        for mid in ids:
            m = self.db.execute('SELECT id,nome,url,tipo,estado FROM materiais WHERE id=?', (mid,)).fetchone()
            if not m: raise ValueError('Uma fonte foi removida. Atualize a seleção.')
            resultado.append(dict(m))
        return resultado

    def salvar(self, d):
        aid = d.get('id'); anterior = self.editavel(aid) if aid else None
        destino = d.get('caderno'); destino = identificador(destino) if destino is not None else None; Cadernos(self.h).validar_destino(destino)
        content = validar_conteudo(d.get('conteudo'))
        if anterior and d.get('versao') != anterior['versao']: raise ValueError('A atividade mudou. Reabra o editor antes de salvar.')
        fontes = self.fontes(d.get('materiais', [f['id'] for f in anterior['fontes'] if f['disponivel']] if anterior else []))
        permitidas = {f['id'] for f in fontes}
        # Mantém referência antiga removida ao editar, mas não permite fabricar novas.
        antigas = {json.dumps(r, sort_keys=True) for q in anterior['conteudo']['exercicios'] for r in q['referencias']} if anterior else set()
        for q in content['exercicios']:
            for r in q['referencias']:
                if r['material_id'] not in permitidas and json.dumps(r, sort_keys=True) not in antigas:
                    raise ValueError('Referência não vinculada aos materiais escolhidos.')
        origem_chat = anterior['origem_chat'] if anterior else d.get('origem_chat')
        titulo_chat = anterior['origem_titulo'] if anterior else self.h.obter(origem_chat)['titulo'] if origem_chat and not d.get('proposta') else ''
        proveniencia = anterior['proveniencia'] if anterior else {}; origem = anterior['origem'] if anterior else 'manual'
        if not anterior and d.get('proposta'):
            job = self.db.execute("SELECT * FROM atividade_jobs WHERE id=? AND tipo='geracao' AND estado='concluida'", (identificador(d['proposta']),)).fetchone()
            if not job: raise ValueError('Proposta indisponível. Gere novamente ou crie manualmente.')
            prev = json.loads(job['previa']); proveniencia = {'provedor': prev['provedor'], 'modelo': prev['modelo'], 'pedido': prev['pedido'], 'fontes': prev['materiais'], 'criado': job['criado']}
            origem = 'ia'
            origem_chat = prev.get('origem_chat')
            if origem_chat and not self.db.execute('SELECT 1 FROM conversas WHERE id=?', (origem_chat,)).fetchone(): origem_chat = None
            titulo_chat = prev.get('origem_titulo', titulo_chat)

        # Nomes/IDs antigos permanecem como proveniência, sem restaurar arquivos removidos.
        fontes_reg = {f['id']: f for f in (anterior['fontes'] if anterior else [])}
        fontes_reg.update({f['id']: f for f in fontes})
        aid = aid or str(uuid4()); v = anterior['versao'] + 1 if anterior else 1
        encoded = json.dumps(content, ensure_ascii=False)
        with self.db:
            if anterior:
                self.db.execute('UPDATE atividades SET caderno_id=?,conteudo=?,versao=?,fontes=?,atualizado=CURRENT_TIMESTAMP WHERE id=?',
                                (destino, encoded, v, json.dumps(list(fontes_reg.values())), aid))
            else:
                self.db.execute('INSERT INTO atividades(id,caderno_id,origem_chat,origem_titulo,origem,fontes,proveniencia,versao,conteudo) VALUES(?,?,?,?,?,?,?,?,?)',
                                (aid, destino, origem_chat, titulo_chat, origem, json.dumps(fontes), json.dumps(proveniencia), v, encoded))
            self.db.execute('INSERT INTO atividade_versoes(atividade_id,versao,conteudo) VALUES(?,?,?)', (aid, v, encoded))
        return self.obter(aid)

    def listar(self, d):
        busca = texto(d.get('busca', ''), 300).casefold(); formato = d.get('formato', ''); dificuldade = d.get('dificuldade', ''); situacao = d.get('situacao', 'ativas')
        if formato not in ('', *FORMATOS) or dificuldade not in ('', *DIFICULDADES) or situacao not in ('ativas', 'arquivadas', 'andamento', 'finalizadas'):
            raise ValueError('Filtro de atividade inválido.')
        destino = d.get('caderno'); destino = identificador(destino) if destino is not None else None; Cadernos(self.h).obter(destino) if destino else None
        pagina = d.get('pagina', 0)
        if type(pagina) is not int or not 0 <= pagina <= 100000: raise ValueError('Página inválida.')
        lista = []
        for row in self.db.execute('SELECT id FROM atividades WHERE caderno_id IS ? AND arquivada=? ORDER BY atualizado DESC,rowid DESC', (destino, int(situacao == 'arquivadas'))):
            a = self.obter(row['id']); con = a['conteudo']
            if busca and busca not in ' '.join(con[k] for k in ['titulo', 'descricao', 'assuntos', 'etiquetas']).casefold(): continue
            if dificuldade and con['dificuldade'] != dificuldade: continue
            if formato and not any(q['formato'] == formato for q in con['exercicios']): continue
            ts = [dict(r) for r in self.db.execute('SELECT id,estado FROM tentativas WHERE atividade_id=? ORDER BY rowid DESC', (a['id'],))]
            if situacao in ['andamento', 'finalizadas'] and not any(t['estado'] == ('andamento' if situacao == 'andamento' else 'finalizada') for t in ts): continue
            a['tentativas'] = len(ts); a['em_andamento'] = next((t['id'] for t in ts if t['estado'] == 'andamento'), None)
            # Listagem não transporta gabaritos.
            a['quantidade'] = len(con['exercicios']); a['formatos'] = sorted({q['formato'] for q in con['exercicios']}); a['conteudo'] = {k:v for k,v in con.items() if k != 'exercicios'}
            lista.append(a)
        pagina = min(pagina, max(0, (len(lista)-1)//30))
        return {'itens': lista[pagina*30:(pagina+1)*30], 'total': len(lista), 'pagina': pagina}

    def acao(self, d):
        a = self.obter(d.get('id')); acao = d.get('acao')
        if acao == 'arquivar':
            if type(d.get('valor')) is not bool: raise ValueError('Estado inválido.')
            if a['caderno_arquivado']: raise ValueError('Restaure o caderno para alterar a atividade.')
            with self.db: self.db.execute('UPDATE atividades SET arquivada=? WHERE id=?', (int(d['valor']), a['id']))
        elif acao == 'mover':
            self.editavel(a['id']); Cadernos(self.h).validar_destino(d.get('destino'))
            with self.db: self.db.execute('UPDATE atividades SET caderno_id=?,atualizado=CURRENT_TIMESTAMP WHERE id=?', (d.get('destino'), a['id']))
        elif acao == 'duplicar':
            destino = d.get('destino', a['caderno_id']); Cadernos(self.h).validar_destino(destino)
            content = deepcopy(a['conteudo']); content['titulo'] = content['titulo'][:172]+' (cópia)'
            novo = str(uuid4()); encoded = json.dumps(content, ensure_ascii=False)
            with self.db:
                self.db.execute('INSERT INTO atividades(id,caderno_id,origem_chat,origem_titulo,origem,fontes,proveniencia,versao,conteudo) VALUES(?,?,?,?,?,?,?,?,?)',
                                (novo, destino, a['origem_chat'], a['origem_titulo'], a['origem'], json.dumps(a['fontes']), json.dumps(a['proveniencia']), 1, encoded))
                self.db.execute('INSERT INTO atividade_versoes(atividade_id,versao,conteudo) VALUES(?,1,?)', (novo, encoded))
            return self.obter(novo)
        else: raise ValueError('Ação inválida. Arquive para preservar o histórico.')
        return self.obter(a['id'])

    def navegar(self, d):
        atual = self.navegacao(); area = d.get('area', 'atividades'); aid = d.get('atividade', atual['atividade']); tid = d.get('tentativa', atual['tentativa'])
        if area not in ('chat', 'materiais', 'atividades'): raise ValueError('Área inválida.')
        if aid: self.obter(aid)
        if tid:
            row = self.db.execute('SELECT atividade_id FROM tentativas WHERE id=?', (identificador(tid),)).fetchone()
            if not row or row['atividade_id'] != aid: raise ValueError('Tentativa não pertence à atividade escolhida.')
        with self.db: self.db.execute('UPDATE estudo_navegacao SET area=?,atividade=?,tentativa=? WHERE id=1', (area, aid, tid))
        return self.navegacao()

    def navegacao(self): return dict(self.db.execute('SELECT * FROM estudo_navegacao WHERE id=1').fetchone())
