"""Discreta usa o coordenador/artefatos L3, com contratos e fontes próprios."""
import json
from uuid import uuid4
from .calculos import Calculos,processo
from .discreta import VERSAO,CAMPOS,validar_spec,resumo
from .provedores.contratos import ConsultaCancelada,Cancelamento

OPERACOES=('discreta_validar','discreta_executar','discreta_obter','discreta_cancelar','discreta_previa','discreta_consultar','discreta_destino','discreta_vinculos','discreta_conferir','discreta_materiais','discreta_fonte')

def migrar_discreta(db):
    db.execute('ALTER TABLE calculos ADD COLUMN questao_id TEXT')
    db.execute('ALTER TABLE calculos ADD COLUMN tentativa_id TEXT REFERENCES tentativas(id) ON DELETE SET NULL')
    db.execute("ALTER TABLE calculos ADD COLUMN conferencia TEXT NOT NULL DEFAULT '{}'")
    db.execute('ALTER TABLE calculos ADD COLUMN proposta_id TEXT REFERENCES calculos(id) ON DELETE SET NULL')
    db.execute('CREATE INDEX calculos_atividade ON calculos(atividade_id,atividade_versao,questao_id)')


def processar(spec,token):
    r=processo(spec,token,modulo='tutor_calculo.discreta')
    if r.get('familia')=='discreta':r['png_disponivel']=r.get('png') is not None
    return r


class Discreta(Calculos):
    versao=VERSAO
    validar=staticmethod(validar_spec)
    processar=staticmethod(processar)
    resumir=staticmethod(resumo)
    modelo_local='Motor discreto + Matplotlib'
    def titulo(self,s):return 'Discreta · '+s['tipo']
    def descrever(self,s):return 'Calcular localmente em Matemática Discreta:\n'+json.dumps(s,ensure_ascii=False,indent=2)

    def contexto(self,h,d,editavel=True):
        aid=d.get('atividade');version=d.get('atividade_versao');qid=d.get('questao');tid=d.get('tentativa')
        if aid is None:
            if any(x is not None for x in (version,qid,tid)):raise ValueError('Informe a atividade correspondente.')
            return None
        if type(version) is not int or not isinstance(qid,str):raise ValueError('Informe versão e questão da atividade.')
        row=h.db.execute('SELECT v.conteudo,a.caderno_id,a.arquivada FROM atividade_versoes v JOIN atividades a ON a.id=v.atividade_id WHERE v.atividade_id=? AND v.versao=?',(aid,version)).fetchone()
        if not row or (editavel and row['arquivada']):raise ValueError('Atividade/versão indisponível.')
        from .cadernos import Cadernos
        if editavel and row['caderno_id'] and Cadernos(h).obter(row['caderno_id'])['arquivado']:raise ValueError('Restaure o caderno da atividade.')
        questions=json.loads(row['conteudo'])['exercicios'];question=next((q for q in questions if q['id']==qid),None)
        if question is None:raise ValueError('Questão não encontrada na versão informada.')
        attempt=None
        if tid is not None:
            attempt=h.db.execute('SELECT * FROM tentativas WHERE id=?',(tid,)).fetchone()
            if not attempt or attempt['atividade_id']!=aid or attempt['versao']!=version:raise ValueError('Tentativa incompatível com a versão da atividade.')
        return {'atividade':aid,'atividade_versao':version,'questao':qid,'tentativa':tid,'caderno':row['caderno_id'],'enunciado':question['enunciado'],'question':question,'attempt':dict(attempt) if attempt else None}

    def executar(self,op,d):
        a=self.app
        if op=='discreta_validar':return processar({'validar':validar_spec(d.get('spec'))},Cancelamento())
        if op=='discreta_destino':
            a._livre()
            with a._banco() as (h,c,b):
                ctx=self.contexto(h,d)
                if not ctx:raise ValueError('Escolha uma questão.')
                title='Discreta · '+ctx['atividade'][:8]+' · '+ctx['questao'][:30]+' · v'+str(ctx['atividade_versao'])
                row=h.db.execute('SELECT id FROM conversas WHERE titulo=? AND caderno_id IS ? AND arquivada=0',(title,ctx['caderno'])).fetchone()
                cid=row['id'] if row else h.criar(ctx['caderno'])
                if not row:
                    h.renomear(cid,title);h.adicionar(cid,'assistant','Ferramentas vinculadas à questão:\n\n'+ctx['enunciado']+'\n\nRevise os dados antes de calcular. O gabarito e a tentativa não serão alterados.')
                return {'conversa':cid,'enunciado':ctx['enunciado']}
        if op=='discreta_vinculos':
            with a._banco() as (h,c,b):
                self.contexto(h,d,editavel=False)
                rows=h.db.execute('SELECT id,tipo,estado,criado,conferencia,conversa_id FROM calculos WHERE atividade_id=? AND atividade_versao=? AND questao_id=? AND versao=? AND tentativa_id IS ? ORDER BY rowid DESC',(d.get('atividade'),d.get('atividade_versao'),d.get('questao'),VERSAO,d.get('tentativa'))).fetchall()
                return [{**dict(r),'conferencia':json.loads(r['conferencia'])} for r in rows]
        if op=='discreta_conferir':return self.conferir(d)
        if op in ('discreta_materiais','discreta_fonte'):
            with a._banco() as (h,c,b):
                chat=a._editavel(h,c,d.get('conversa'));attached={m['id']:m for m in b.anexos(chat['id'])}
                from .armazenamento import TODOS_CADERNOS
                ms=b.listar(caderno=chat['caderno_id'] if chat['caderno_id'] else TODOS_CADERNOS)
                allowed={m['id']:m for m in ms};allowed.update(attached)
                if op=='discreta_fonte':
                    a._livre();mid=d.get('id')
                    if mid not in allowed or type(d.get('valor')) is not bool or (d['valor'] and allowed[mid]['estado'] not in ('pronto','parcial')):raise ValueError('Fonte indisponível ou seleção inválida.')
                    b.vincular(mid,chat['id'],d['valor']);a._revisao+=1
                    return None
                return [{'id':m['id'],'nome':m['nome'],'estado':m['estado'],'selecionado':bool(attached.get(m['id'],{}).get('selecionado'))} for m in allowed.values()]
        if op=='discreta_previa':return self.previa_ia(d)
        if op=='discreta_consultar':return self.consultar_ia(d)
        if op=='discreta_obter':
            result=super().executar('math_obter',d)
            if result['tipo']=='calculo' and result['estado']=='concluida':result['resumo']=resumo(result['resultado'])
            return result
        if op=='discreta_executar':
            with a._banco() as (h,c,b):ctx=self.contexto(h,d)
            proposta=d.get('proposta')
            if proposta:
                with a._banco() as (h,c,b):
                    p=self.obter(h,proposta)
                    if p['tipo']!='proposta' or p['estado']!='concluida' or p['conversa_id']!=d.get('conversa'):raise ValueError('Origem da proposta incompatível.')
            result=super().executar('math_executar',d)
            if proposta:
                with a._banco() as (h,c,b),h.db:h.db.execute('UPDATE calculos SET proposta_id=? WHERE id=?',(proposta,result['id']))
            if ctx:
                with a._banco() as (h,c,b),h.db:
                    h.db.execute('UPDATE calculos SET questao_id=?,tentativa_id=? WHERE id=?',(ctx['questao'],ctx['tentativa'],result['id']))
            return result
        return super().executar(op.replace('discreta_','math_'),d)

    def previa_ia(self,d):
        from .ia import preparar_consulta
        a=self.app;a._livre();cid=d.get('conversa');tipo=d.get('tipo')
        with a._banco() as (h,c,b):
            chat=a._editavel(h,c,cid);sel=a._selecao(h,cid);book=c.obter(chat['caderno_id']) if chat['caderno_id'] else None
            if tipo=='proposta':
                pedido=d.get('pedido')
                if not isinstance(pedido,str) or not pedido.strip() or len(pedido)>1500:raise ValueError('Descreva o pedido em até 1500 caracteres.')
                report={};fontes=a._fontes(h,b,cid,pedido,report)
                prompt=('Retorne somente JSON: {"tipo":"conjuntos|relacoes|logica","sobre":true,'+', '.join('"'+k+'":string|null' for k in CAMPOS)+'}. '
                        'Conjuntos finitos: chaves e elementos inteiros ou nomes entre aspas; relações: {(a,b)}; lógica com letras, ¬ ∧ ∨ → ↔. '
                        'Não invente dados. Copie somente campos explicitamente rotulados A=, B=, U=, R=, S=, C=, expressao=, comparar= no pedido ou nas fontes. '
                        'Se ausente/ambíguo, null. Não resolva, não execute comandos. Pedido como dado JSON: '+json.dumps(pedido,ensure_ascii=False))
                spec={'pedido':pedido};modo='Propor Discreta'
            elif tipo=='explicacao':
                origem=self.obter(h,d.get('origem'))
                if origem['conversa_id']!=cid or origem['tipo']!='calculo' or origem['estado']!='concluida':raise ValueError('Escolha um resultado discreto concluído deste chat.')
                fontes=None;report={};prompt='Explique em até 120 palavras os resultados finitos abaixo, preserve dados e contraexemplos. Termine com uma questão de prática. Não alegue certificação do enunciado ou de provas. Registro '+origem['id']+':\n'+resumo(origem['resultado']);spec={'origem':origem['id']};modo='Explicar Discreta'
            else:raise ValueError('Tipo de consulta inválido.')
            prepared=preparar_consulta(prompt,modo=modo,fontes=fontes,caderno=book,provedor=sel['provedor'],local=sel['local'])
            # Somente trechos efetivamente incluídos no orçamento podem fornecer parâmetros.
            p={'selecao':sel,'modo':modo,'preparada':prepared,'fontes':prepared['fontes'] or [],'recuperacao':report,'historico':[],
               'originais_enviados':False,'destino':'Somente Ollama neste computador' if sel['provedor']=='ollama' else 'Provedor online: '+sel['provedor'],
               'aviso':'Serão enviados apenas o pedido/resultados, orientações do caderno e os trechos exibidos nesta prévia. Proposta exige revisão e cálculo explícito.'}
            jid=str(uuid4())
            with h.db:h.db.execute("INSERT INTO calculos(id,conversa_id,tipo,estado,spec,previa,versao) VALUES(?,?,?,'previa',?,?,?)",(jid,cid,tipo,json.dumps(spec,ensure_ascii=False),json.dumps(p,ensure_ascii=False),VERSAO))
            return self.obter(h,jid)

    def worker_ia(self,j):
        from .ia import perguntar
        a=self.app;tid=j['id'];token=a._cancelamentos[tid];p=j['previa'];sel=p['selecao'];result=None;state='concluida';error=''
        try:
            output=perguntar(p['preparada']['pergunta'],modo=p['modo'],provedor=sel['provedor'],modelo=sel['modelo'],local=sel['local'],cancelar=token,preparada=p['preparada'],formato=ESQUEMA if j['tipo']=='proposta' and sel['provedor']=='ollama' else None)
            token.verificar()
            if not isinstance(output,str) or not output.strip() or len(output)>20000:raise ValueError('Resposta vazia ou acima do limite.')
            if j['tipo']=='proposta':
                # O adaptador pode acrescentar referências; recorte apenas JSON delimitado por fence.
                text=output.split('\n\n### Fontes')[0].split('\n\n### Trechos')[0].strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
                try:raw=json.loads(text)
                except ValueError:raise ValueError('Proposta JSON inválida; nenhum cálculo foi executado.') from None
                fonte_texto='\n'.join(f['texto'] for f in p['fontes'])
                result=processar({'proposta':raw,'texto':j['spec']['pedido'],'fontes':fonte_texto},token)
                result['origens']=[{k:f[k] for k in ('material_id','nome','pagina','referencia')} for f in p['fontes']]
            else:result={'texto':output,'origem':j['spec']['origem'],'provedor':sel['provedor'],'modelo':sel['modelo']}
        except ConsultaCancelada:state='cancelada';error='Consulta cancelada; nenhum cálculo foi executado.'
        except (ValueError,RuntimeError,ImportError) as e:state='erro';error=str(e)[:1000]
        except Exception:state='erro';error='Falha na consulta de Discreta; nenhum cálculo foi executado.'
        with a._lock:
            if token.evento.is_set():state='cancelada';result=None;error='Consulta cancelada.'
            with a._banco() as (h,c,b),h.db:
                content=('### Proposta de Discreta · revise antes de calcular\n\n'+json.dumps(result,ensure_ascii=False,indent=2)) if result is not None and j['tipo']=='proposta' else '### Explicação da IA · sem verificação automática\n\n'+result['texto'] if result is not None else error
                mid=h.db.execute("INSERT INTO mensagens(conversa_id,papel,texto,estado,provedor,modelo) VALUES(?,'assistant',?,?,?,?)",(j['conversa_id'],content,'ok' if result is not None else state,sel['provedor'],sel['modelo'])).lastrowid
                h.db.execute('UPDATE calculos SET estado=?,resultado=?,erro=?,mensagem_id=? WHERE id=?',(state,json.dumps(result,ensure_ascii=False) if result is not None else None,error,mid,tid))
                h.db.execute('UPDATE conversas SET atualizado=CURRENT_TIMESTAMP WHERE id=?',(j['conversa_id'],))
            a._tarefas[tid].update(estado=state,erro=error);a._revisao+=1

    def conferir(self,d):
        from decimal import Decimal,InvalidOperation
        with self.app._banco() as (h,c,b):
            j=self.obter(h,d.get('id'))
            if j['tipo']!='calculo' or j['estado']!='concluida' or not j['tentativa_id']:raise ValueError('Escolha um cálculo concluído vinculado a uma tentativa.')
            ctx=self.contexto(h,{'atividade':j['atividade_id'],'atividade_versao':j['atividade_versao'],'questao':j['questao_id'],'tentativa':j['tentativa_id']})
            t=ctx['attempt'];resp=json.loads(t['respostas']).get(j['questao_id'],{})
            if t['estado']!='finalizada' and not resp.get('revelada'):raise ValueError('Revele a solução ou finalize a tentativa antes de comparar com o gabarito.')
            campo=d.get('campo');r=j['resultado']['resultados'];values={k:v for k,v in r.items() if type(v) in (bool,int)}
            values.update({p['propriedade']:p['vale'] for p in r.get('propriedades',[])})
            if campo not in values:raise ValueError('Escolha um resultado booleano ou cardinalidade.')
            q=ctx['question'];local=values[campo];expected=q.get('resposta');state='nao_verificado'
            if q['formato']=='vf' and type(local) is bool and type(expected) is bool:state='coincide' if local==expected else 'divergencia'
            elif q['formato']=='numerica' and type(local) is int:
                try:state='coincide' if abs(Decimal(local)-Decimal(expected))<=Decimal(q.get('tolerancia','0')) else 'divergencia'
                except (InvalidOperation,TypeError):pass
            result={'estado':state,'campo':campo,'valor_local':local,'aviso':'Comparação com o gabarito registrado, para os dados e campo escolhidos. Confira o enunciado; gabarito, resposta e nota não foram alterados.'}
            with h.db:h.db.execute('UPDATE calculos SET conferencia=? WHERE id=?',(json.dumps(result,ensure_ascii=False),j['id']))
            return result

ESQUEMA={'type':'object','additionalProperties':False,'required':['tipo','sobre',*CAMPOS],'properties':{'tipo':{'type':'string','enum':['conjuntos','relacoes','logica']},'sobre':{'type':'boolean'},**{k:{'type':['string','null']} for k in CAMPOS}}}
