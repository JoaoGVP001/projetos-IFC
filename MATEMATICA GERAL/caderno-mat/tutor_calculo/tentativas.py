"""Tentativas persistentes com snapshot desde o início e finalização idempotente."""
import json
from uuid import uuid4
from .atividades import Atividades, identificador, texto
from .correcao import corrigir, resumo, validar_resposta
from .cadernos import Cadernos


class Tentativas:
    def __init__(self, h): self.h, self.db, self.atividades = h, h.db, Atividades(h)

    def _obter(self, tid):
        row = self.db.execute('SELECT * FROM tentativas WHERE id=?', (identificador(tid),)).fetchone()
        if not row: raise ValueError('Tentativa não encontrada.')
        t = dict(row)
        for k in ['snapshot', 'respostas', 'resultado']: t[k] = json.loads(t[k])
        return t

    def _editavel(self, tid, finalizada=False):
        t = self._obter(tid); self.atividades.editavel(t['atividade_id'])
        if not finalizada and t['estado'] != 'andamento': raise ValueError('Tentativa finalizada. Inicie uma nova para responder novamente.')
        return t

    def _q(self, t, qid):
        q = next((q for q in t['snapshot']['conteudo']['exercicios'] if q['id'] == qid), None)
        if not q: raise ValueError('Exercício não pertence a esta tentativa.')
        return q

    def _gravar(self, t):
        with self.db: self.db.execute('UPDATE tentativas SET respostas=?,posicao=? WHERE id=?', (json.dumps(t['respostas'], ensure_ascii=False), t['posicao'], t['id']))

    def iniciar(self, aid, nova=False):
        a = self.atividades.editavel(aid)
        if not nova:
            row = self.db.execute("SELECT id FROM tentativas WHERE atividade_id=? AND estado='andamento' ORDER BY rowid DESC LIMIT 1", (aid,)).fetchone()
            if row: return self.obter(row['id'])
        tid = str(uuid4()); snap = {'conteudo': a['conteudo'], 'fontes': a['fontes'], 'origem': a['origem'], 'proveniencia': a['proveniencia'],
                                   'caderno': Cadernos(self.h).obter(a['caderno_id'])['nome'] if a['caderno_id'] else 'Geral'}
        with self.db:
            self.db.execute('INSERT INTO tentativas(id,atividade_id,versao,snapshot) VALUES(?,?,?,?)', (tid, aid, a['versao'], json.dumps(snap, ensure_ascii=False)))
        return self.obter(tid)

    def obter(self, tid):
        t = self._obter(tid); a = self.atividades.obter(t['atividade_id']); final = t['estado'] == 'finalizada'
        t['resumo'] = resumo(t['snapshot']['conteudo']['exercicios'], t['respostas'], final)
        t['editavel'] = not a['arquivada'] and not a['caderno_arquivado']; t['versao_atual'] = a['versao']
        for f in t['snapshot']['fontes']:
            f['disponivel'] = bool(self.db.execute('SELECT 1 FROM materiais WHERE id=?', (f['id'],)).fetchone())
        for q in t['snapshot']['conteudo']['exercicios']:
            r = t['respostas'].get(q['id'], {})
            q['solucao_disponivel'] = bool(q['explicacao'] or q['resposta'] is not None and q['resposta'] != '')
            if not final and not r.get('revelada'):
                q.pop('resposta', None); q.pop('explicacao', None)
        return t

    def salvar(self, d):
        t = self._editavel(d.get('id')); pos = d.get('posicao', t['posicao'])
        if type(pos) is not int or not 0 <= pos < len(t['snapshot']['conteudo']['exercicios']): raise ValueError('Posição inválida.')
        if 'exercicio' in d:
            q = self._q(t, d['exercicio']); r = t['respostas'].setdefault(q['id'], {})
            r['resposta'] = validar_resposta(q, d.get('resposta'))
        t['posicao'] = pos; self._gravar(t)
        return self.obter(t['id'])

    def navegar(self, d):
        t = self._obter(d.get('id')); pos = d.get('posicao')
        if type(pos) is not int or not 0 <= pos < len(t['snapshot']['conteudo']['exercicios']): raise ValueError('Posição inválida.')
        with self.db: self.db.execute('UPDATE tentativas SET posicao=? WHERE id=?', (pos, t['id']))
        return self.obter(t['id'])

    def revelar(self, tid, qid):
        t = self._editavel(tid); self._q(t, qid)
        t['respostas'].setdefault(qid, {})['revelada'] = True; self._gravar(t)
        return self.obter(tid)

    def finalizar(self, tid, confirmado=False):
        t = self._obter(tid)
        if t['estado'] == 'finalizada': return self.obter(tid)
        self._editavel(tid)
        qs = t['snapshot']['conteudo']['exercicios']; s = resumo(qs, t['respostas'])
        brancas = len(qs)-s['respondidas']
        if brancas and not confirmado: raise ValueError(f'{brancas} questão(ões) sem resposta. Confirme para finalizar mesmo assim.')
        resultado = {q['id']: corrigir(q, t['respostas'].get(q['id'], {})) for q in qs}
        with self.db: self.db.execute("UPDATE tentativas SET estado='finalizada',fim=CURRENT_TIMESTAMP,resultado=? WHERE id=? AND estado='andamento'", (json.dumps(resultado), tid))
        return self.obter(tid)

    def revisar(self, d):
        t = self._editavel(d.get('id'), True); q = self._q(t, d.get('exercicio'))
        if t['estado'] != 'finalizada': raise ValueError('Finalize antes de registrar revisão manual.')
        if t['resultado'][q['id']]['estado'] in ('correta', 'incorreta'): raise ValueError('Questão já corrigida objetivamente; o resultado local permanece.')
        avaliacao = d.get('avaliacao', 'observacao')
        if avaliacao not in ('adequada', 'revisar', 'observacao'): raise ValueError('Avaliação manual inválida.')
        t['respostas'].setdefault(q['id'], {})['revisao'] = {'avaliacao': avaliacao, 'texto': texto(d.get('texto'), 8000, True)}
        self._gravar(t); return self.obter(t['id'])

    def historico(self, aid):
        self.atividades.obter(aid); lista = []
        for row in self.db.execute('SELECT id FROM tentativas WHERE atividade_id=? ORDER BY rowid DESC', (aid,)):
            t = self._obter(row['id']); lista.append({k:t[k] for k in ['id', 'versao', 'estado', 'inicio', 'fim']} | {'resumo': resumo(t['snapshot']['conteudo']['exercicios'], t['respostas'], t['estado'] == 'finalizada')})
        return lista

    def comparar(self, ids):
        if not isinstance(ids, list) or len(ids) != 2 or ids[0] == ids[1]: raise ValueError('Escolha duas tentativas diferentes.')
        ts = [self._obter(i) for i in ids]
        if ts[0]['atividade_id'] != ts[1]['atividade_id']: raise ValueError('Compare tentativas da mesma atividade.')
        return {'mesma_versao': ts[0]['versao'] == ts[1]['versao'], 'tentativas': [self.obter(i) for i in ids]}

    def ajuda_chat(self, tid, qid):
        t = self._obter(tid); self.atividades.editavel(t['atividade_id']); q = self._q(t, qid)
        a = self.atividades.obter(t['atividade_id']); cid = self.h.criar(a['caderno_id'])
        dados = {'atividade': t['snapshot']['conteudo']['titulo'], 'versao': t['versao'], 'enunciado': q['enunciado'],
                 'alternativas': q['alternativas'], 'resposta_do_aluno': t['respostas'].get(qid, {}).get('resposta')}
        self.h.renomear(cid, 'Ajuda: '+t['snapshot']['conteudo']['titulo'][:80])
        self.h.rascunho(cid, 'Me dê uma dica progressiva sobre este exercício, sem revelar a solução.\n\n'+json.dumps(dados, ensure_ascii=False))
        Cadernos(self.h).salvar_navegacao(a['caderno_id'], cid)
        self.atividades.navegar({'area': 'chat'})
        return cid
