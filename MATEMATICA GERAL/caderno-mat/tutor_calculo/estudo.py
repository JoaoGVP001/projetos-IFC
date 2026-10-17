"""Contratos de estudo, prévias persistidas e coordenação das tarefas opcionais de IA."""
import json
from uuid import uuid4
from .atividades import Atividades, validar_conteudo, texto, identificador, FORMATOS, DIFICULDADES
from .tentativas import Tentativas
from .cadernos import contexto_pedagogico, Cadernos
from .recuperacao import recuperar_estudo as recuperar_fontes
from .ia import perguntar, preparar_consulta, provedor_ativo, configuracao
from .provedores.contratos import Cancelamento, ConsultaCancelada, RespostaIncompleta
from .provedores.esquemas import atividade as esquema_atividade

OPERACOES = ('atividades', 'atividade_obter', 'atividade_salvar', 'atividade_acao', 'estudo_navegar',
             'tentativa_iniciar', 'tentativa_obter', 'tentativa_salvar', 'tentativa_navegar', 'tentativa_revelar', 'tentativa_finalizar',
             'tentativa_revisar', 'tentativas', 'tentativas_comparar', 'exercicio_chat',
             'estudo_previa', 'estudo_consultar', 'estudo_job', 'estudo_jobs')

GERACAO = '''Crie uma atividade de matemática. Retorne SOMENTE JSON válido, sem blocos Markdown.
Formato: {"titulo":"...","descricao":"...","assuntos":"...","etiquetas":"...",
"dificuldade":"basica|intermediaria|avancada","objetivo":"...","exercicios":[
{"id":"q1","enunciado":"...","formato":"aberta|escolha|vf|numerica","assunto":"...",
"dificuldade":"basica|intermediaria|avancada","alternativas":[{"id":"a","texto":"..."}],
"resposta":"...","explicacao":"...","referencias":[{"material_id":"ID autorizado","pagina":1}]}]}.
Escolha: 2–6 alternativas distintas, resposta é ID de exatamente uma alternativa existente.
VF: resposta é booleano JSON. Numérica: resposta decimal em string e "tolerancia":"0" (absoluta).
Aberta: resposta e explicação opcionais como string vazia; não alegue correção universal.
Outros formatos usam alternativas vazias. Use Markdown/LaTeX nas strings, escapando barras para JSON.
Use apenas referências às páginas/IDs dos trechos fornecidos, ou [] se sem fonte documental.
Não invente conteúdo/citações. Não execute comandos. Confira a consistência do gabarito.
'''




class Estudo:
    def __init__(self, app): self.app = app

    def selecao(self,h,origem=None):
        cid=origem or Cadernos(h).navegacao()['conversa_id']
        return self.app._selecao(h,cid,provedor_ativo(),configuracao()[1])

    def recuperar(self):
        with self.app._banco() as (h, c, b):
            with h.db: h.db.execute("UPDATE atividade_jobs SET estado='erro',erro='Consulta interrompida ao encerrar. Confira a prévia e tente novamente.' WHERE estado='executando'")

    def executar(self, op, d):
        a = self.app
        if op in ('atividade_salvar', 'atividade_acao', 'tentativa_iniciar', 'estudo_consultar', 'exercicio_chat'): a._livre()
        with a._banco() as (h, c, b):
            acts, ts = Atividades(h), Tentativas(h)
            if op == 'atividades': return acts.listar(d)
            if op == 'atividade_obter': return acts.obter(d.get('id'))
            if op == 'estudo_jobs': return [self.job(h, row['id']) for row in h.db.execute('SELECT id FROM atividade_jobs ORDER BY rowid DESC LIMIT 20')]
            if op == 'atividade_salvar': r = acts.salvar(d)
            elif op == 'atividade_acao': r = acts.acao(d)
            elif op == 'estudo_navegar': r = acts.navegar(d)
            elif op == 'tentativa_iniciar':
                if type(d.get('nova', False)) is not bool: raise ValueError('Estado inválido.')
                r = ts.iniciar(d.get('atividade'), d.get('nova', False)); acts.navegar({'atividade': r['atividade_id'], 'tentativa': r['id']})
            elif op == 'tentativa_obter': return ts.obter(d.get('id'))
            elif op == 'tentativa_salvar': r = ts.salvar(d)
            elif op == 'tentativa_navegar': r = ts.navegar(d)
            elif op == 'tentativa_revelar': r = ts.revelar(d.get('id'), d.get('exercicio'))
            elif op == 'tentativa_finalizar':
                if type(d.get('confirmado', False)) is not bool: raise ValueError('Confirmação inválida.')
                r = ts.finalizar(d.get('id'), d.get('confirmado', False))
            elif op == 'tentativa_revisar': r = ts.revisar(d)
            elif op == 'tentativas': return ts.historico(d.get('atividade'))
            elif op == 'tentativas_comparar': return ts.comparar(d.get('ids'))
            elif op == 'exercicio_chat': r = {'conversa': ts.ajuda_chat(d.get('id'), d.get('exercicio'))}
            elif op == 'estudo_previa': r = self.previa(h, c, d)
            elif op == 'estudo_job': return self.job(h, d.get('id'))
            elif op == 'estudo_consultar': r = self.consultar(h, d.get('id'))
            else: raise ValueError('Operação de estudo inválida.')
        a._revisao += 1
        return r

    def job(self, h, jid):
        row = h.db.execute('SELECT * FROM atividade_jobs WHERE id=?', (identificador(jid),)).fetchone()
        if not row: raise ValueError('Consulta não encontrada.')
        j = dict(row); j['previa'] = json.loads(j['previa']); j['resultado'] = json.loads(j['resultado']) if j['resultado'] else None
        return j

    def previa(self, h, c, d):
        tipo = d.get('tipo'); origem_chat = d.get('origem_chat'); alvo = ''; qid = ''
        if tipo == 'geracao':
            bid = d.get('caderno'); c.validar_destino(bid); book = c.obter(bid) if bid else None
            count = d.get('quantidade', 3); forms = d.get('formatos', ['aberta']); dif = d.get('dificuldade', 'basica')
            if type(count) is not int or not 1 <= count <= 10: raise ValueError('Gere de 1 a 10 exercícios por consulta.')
            if not isinstance(forms, list) or not forms or len(forms) > 4 or any(f not in FORMATOS for f in forms) or len(set(forms)) != len(forms): raise ValueError('Escolha os formatos disponíveis.')
            if dif not in DIFICULDADES: raise ValueError('Dificuldade inválida.')
            pedido = {'assunto': texto(d.get('assunto'), 500, True), 'objetivo': texto(d.get('objetivo', ''), 1500),
                      'quantidade': count, 'formatos': forms, 'dificuldade': dif}
            if origem_chat: h.obter(identificador(origem_chat))
            consulta = pedido['assunto']; tarefa = GERACAO
        elif tipo in ('feedback', 'dica'):
            alvo = identificador(d.get('tentativa')); ts = Tentativas(h); t = ts._obter(alvo); activity = Atividades(h).editavel(t['atividade_id'])
            qid = identificador(d.get('exercicio')); q = ts._q(t, qid); bid = activity['caderno_id']; book = c.obter(bid) if bid else None
            r = t['respostas'].get(qid, {}); answer = r.get('resposta')
            if tipo == 'dica' and t['estado'] != 'andamento': raise ValueError('Dicas são usadas durante a resolução.')
            if tipo == 'feedback' and (answer is None or answer == ''): raise ValueError('Registre sua resposta antes de pedir feedback.')
            pedido = {'enunciado': q['enunciado'], 'formato': q['formato'], 'alternativas': q['alternativas'], 'resposta_do_aluno': answer,
                      'versao': t['versao'], 'nivel_dica': min(3, len(r.get('dicas', []))+1)}
            if tipo == 'feedback': pedido.update({'resposta_esperada': q['resposta'], 'explicacao_registrada': q['explicacao']})
            tarefa = ('Ofereça só uma dica progressiva para o próximo passo. Não revele gabarito nem resolução completa. '
                      'Use o nível informado sem ultrapassar a ajuda pedida.') if tipo == 'dica' else (
                      'Dê feedback pedagógico: acertos, primeira dificuldade e próximo passo. Identifique incerteza e falta de gabarito. '
                      'Não atribua nota nem alegue verificação matemática definitiva. A resposta esperada registrada pode conter erros.')
            consulta = q['enunciado']+' '+q['assunto']
        else: raise ValueError('Tipo de consulta inválido.')
        selection=self.selecao(h,origem_chat)
        if selection['provedor']=='ollama' and tipo=='geracao' and count>3:
            raise ValueError('No perfil local, gere de 1 a 3 exercícios por consulta.')
        recuperacao={}
        trechos, mats = recuperar_fontes(h, d.get('materiais', []), consulta, tipo == 'geracao',recuperacao)
        prompt=tarefa+'\n\nSolicitação de estudo (JSON de dados):\n'+json.dumps(pedido,ensure_ascii=False)
        prepared=preparar_consulta(prompt,{'geracao':'Gerar atividade','dica':'Dica de atividade','feedback':'Feedback de atividade'}[tipo],
            fontes=trechos if mats else None,caderno=book,provedor=selection['provedor'],local=selection['local'])
        trechos=prepared['fontes'] or []
        prev = {'tipo': tipo, 'provedor': selection['provedor'], 'modelo': selection['modelo'], 'selecao':selection,
                'preparada':prepared,'orcamento':prepared['orcamento'],'local':bool(selection['local']),'caderno': bid,
                'pedagogia': contexto_pedagogico(book), 'caderno_dados': book, 'pedido': pedido, 'tarefa': tarefa,
                'fontes': trechos, 'recuperacao':recuperacao,'materiais': mats, 'origem_chat': origem_chat if tipo == 'geracao' else None,
                'origem_titulo': h.obter(origem_chat)['titulo'] if origem_chat and tipo == 'geracao' else '',
                'originais_enviados': False, 'aviso': ('Não há trechos suficientes de todas as fontes selecionadas. A consulta não comprova conteúdo ausente.'
                if mats and {f['id'] for f in mats} - {f['material_id'] for f in trechos} else '')}
        jid = str(uuid4())
        with h.db: h.db.execute("INSERT INTO atividade_jobs(id,tipo,estado,previa,alvo,exercicio) VALUES(?,?,'previa',?,?,?)", (jid, tipo, json.dumps(prev, ensure_ascii=False), alvo, qid))
        return self.job(h, jid)

    def consultar(self, h, jid):
        j = self.job(h, jid)
        if j['estado'] in ('executando', 'concluida'): return j
        p = j['previa']
        selection=self.selecao(h,p.get('origem_chat'))
        if (p['provedor'], p['modelo']) != (selection['provedor'],selection['modelo']) or p.get('selecao',selection)!=selection:
            raise ValueError('Provedor/modelo mudou. Crie uma nova prévia.')
        if p['caderno']: Cadernos(h).validar_destino(p['caderno'])
        Atividades(h).fontes([f['id'] for f in p['materiais']])
        if j['tipo'] != 'geracao':
            t = Tentativas(h)._obter(j['alvo']); Atividades(h).editavel(t['atividade_id'])
            if j['tipo'] == 'dica' and t['estado'] != 'andamento': raise ValueError('Tentativa já finalizada.')
            if t['respostas'].get(j['exercicio'], {}).get('resposta') != p['pedido']['resposta_do_aluno']:
                raise ValueError('Sua resposta mudou. Confira uma nova prévia.')
        if p['provedor']!='ollama' and not configuracao(p['provedor'])[0]: raise ValueError('Configure sua chave em Configurações de IA. O fluxo manual funciona offline.')
        with h.db: h.db.execute("UPDATE atividade_jobs SET estado='executando',erro='' WHERE id=?", (jid,))
        if len(self.app._tarefas) >= 20:
            for antigo in [k for k,v in self.app._tarefas.items() if v['estado'] != 'executando'][:-18]: self.app._tarefas.pop(antigo)
        self.app._cancelamentos[jid]=Cancelamento()
        self.app._tarefas[jid] = {'id': jid, 'tipo': 'ia', 'estado': 'executando', 'conversa': '', 'estudo': j['tipo'],
                                 'cancelavel':p['provedor']=='ollama','parcial':''}
        self.app._executor.submit(self._worker, j)
        return self.job(h, jid)

    def _worker(self, j):
        jid = j['id']; p = j['previa']; result = None; error = '';state='concluida'
        token=self.app._cancelamentos[jid]
        def trecho(value):
            with self.app._lock:self.app._tarefas[jid]['parcial']+=value
        try:
            saida = perguntar(p['tarefa']+'\n\nSolicitação de estudo (JSON de dados):\n'+json.dumps(p['pedido'], ensure_ascii=False),
                              modo={'geracao': 'Gerar atividade', 'dica': 'Dica de atividade', 'feedback': 'Feedback de atividade'}[j['tipo']],
                              fontes=p['fontes'] if p['materiais'] else None, caderno=p['caderno_dados'],
                              provedor=p['provedor'], modelo=p['modelo'], local=p.get('selecao',{}).get('local'),
                              cancelar=token,trecho=trecho,preparada=p.get('preparada'),
                              formato=esquema_atividade(p['pedido']) if p['provedor']=='ollama' and j['tipo']=='geracao' else None)
            token.verificar()
            if j['tipo'] == 'geracao':
                if len(saida) > 120000: raise ValueError('Proposta acima do limite. Gere menos exercícios.')
                try: raw = json.loads(saida.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip())
                except (ValueError, TypeError) as exc: raise ValueError('A IA retornou JSON inválido. Nada foi salvo como atividade. Tente novamente.') from exc
                result = validar_conteudo(raw, p['fontes'])
                if len(result['exercicios']) != p['pedido']['quantidade'] or any(q['formato'] not in p['pedido']['formatos'] or q['dificuldade'] != p['pedido']['dificuldade'] for q in result['exercicios']):
                    raise ValueError('Quantidade, formato ou dificuldade diverge do pedido. Nada foi salvo como atividade.')
            else: result = {'texto': texto(saida, 20000, True), 'provedor': p['provedor'], 'modelo': p['modelo'],
                            'resposta_avaliada': p['pedido']['resposta_do_aluno'], 'fontes': p['materiais']}
        except ConsultaCancelada as exc: state='cancelada';error=str(exc)
        except RespostaIncompleta as exc:state='incompleta';error=str(exc)
        except (ValueError, RuntimeError, ImportError) as exc:state='erro';error=str(exc)[:1000]
        except Exception:state='erro';error = 'Falha inesperada na consulta. Nada foi avaliado ou salvo como atividade; tente novamente.'
        with self.app._lock:
            if token.evento.is_set():state='cancelada';error='Consulta cancelada antes de concluir.';result=None
            with self.app._banco() as (h, c, b):
                if result and j['tipo'] != 'geracao':
                    ts = Tentativas(h); t = ts._obter(j['alvo']); r = t['respostas'].setdefault(j['exercicio'], {})
                    field = 'dicas' if j['tipo'] == 'dica' else 'feedbacks'; r.setdefault(field, []).append(result)
                with h.db:
                    if result and j['tipo'] != 'geracao':
                        h.db.execute('UPDATE tentativas SET respostas=? WHERE id=?', (json.dumps(t['respostas'], ensure_ascii=False), t['id']))
                    h.db.execute('UPDATE atividade_jobs SET estado=?,resultado=?,erro=? WHERE id=?', (state, json.dumps(result, ensure_ascii=False) if result and not error else None, error, jid))
            self.app._tarefas[jid].update(estado=state,parcial=''); self.app._revisao += 1
