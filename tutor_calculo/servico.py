"""Coordenacao independente da janela: conexoes por operacao e tarefas isoladas."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
import base64
import io
import json
import os
import subprocess
import sys
from uuid import uuid4
import time

from .armazenamento import Historico, TODOS_CADERNOS, caminho_banco
from .cadernos import Cadernos, contexto_pedagogico
from .materiais import Biblioteca, Extracao, ESTADOS
from .ia import configuracao, limitar_contexto, perguntar, preparar_consulta, provedor_ativo, salvar_configuracao
from .preferencias_ia import PreferenciasIA
from .provedores.contratos import Cancelamento, ConsultaCancelada, RespostaIncompleta
from .provedores.ollama import Ollama, validar_config
from .app import resolver, usa_analisador
from .links import normalizar_url


def texto(valor, limite=1000, vazio=True):
    if not isinstance(valor,str) or len(valor)>limite or '\x00' in valor:
        raise ValueError('Texto invalido ou acima do limite permitido.')
    if not vazio and not valor.strip():raise ValueError('Preencha o campo obrigatorio.')
    return valor


def ident(valor, opcional=False):
    if valor is None and opcional:return None
    return texto(valor,100,False)


def booleano(valor):
    if not isinstance(valor,bool):raise ValueError('Estado invalido.')
    return valor


class Aplicacao:
    def __init__(self,caminho=None):
        self.caminho=Path(caminho) if caminho else caminho_banco()
        self._lock=RLock()
        self._executor=ThreadPoolExecutor(max_workers=3,thread_name_prefix='cadernomat')
        self._tarefas={}
        self._cancelamentos={}
        self._ia_preferencias=PreferenciasIA(self.caminho.parent)
        self._indice_cancelamento=None
        self._processando=set()
        self._revisao=0
        self._fechado=False
        from .estudo import Estudo
        self._estudo=Estudo(self)
        from .calculos import Calculos
        self._calculos=Calculos(self)
        with self._banco() as (h,c,b):
            Biblioteca(h,recuperar=True)
            from .semantica import IndiceSemantico
            IndiceSemantico(h).recuperar_interrupcao()
            nav=c.navegacao()
            if nav['conversa_id'] is None:
                chats=h.listar(caderno=nav['caderno_id'])
                if chats:c.salvar_navegacao(nav['caderno_id'],chats[0]['id'])
        self._estudo.recuperar()
        self._calculos.recuperar()
        self._recuperar_consultas()

    @contextmanager
    def _banco(self):
        h=Historico(self.caminho)
        try:yield h,Cadernos(h),Biblioteca(h)
        finally:h.fechar()

    def _ocupado(self):
        return any(t['tipo'] in ('ia','indice','matematica') and t['estado']=='executando' for t in self._tarefas.values())

    def _livre(self):
        if self._ocupado():raise ValueError('Aguarde a consulta antes de alterar a organizacao.')

    def _editavel(self,h,c,cid):
        chat=h.obter(cid)
        if chat['arquivada'] or (chat['caderno_id'] and c.obter(chat['caderno_id'])['arquivado']):
            raise ValueError('Restaure o chat e seu caderno para continuar.')
        return chat

    def _preferencias(self):
        try:
            dados=json.loads((self.caminho.parent/'interface.json').read_text())
            if not isinstance(dados,dict):raise ValueError('Preferencias invalidas.')
            return {'tema':dados.get('tema','claro') if dados.get('tema') in ['claro','escuro'] else 'claro',
                    'recolhida':bool(dados.get('recolhida',False))}
        except (OSError,ValueError):return {'tema':'claro','recolhida':False}

    def _selecao(self,h=None,cid=None,padrao=None,modelo_padrao=None):
        prefs=self._ia_preferencias.ler()
        provider=prefs['padrao'] or padrao or provedor_ativo()
        model=prefs['ollama']['modelo'] if provider=='ollama' else (modelo_padrao if provider==padrao and modelo_padrao else configuracao(provider)[1])
        local=prefs['ollama'] if provider=='ollama' else None
        scope='padrao'
        if h and cid:
            row=h.db.execute('SELECT * FROM chat_ia WHERE conversa_id=?',(cid,)).fetchone()
            if row:
                provider,model,scope=row['provedor'],row['modelo'],'chat'
                if provider not in ('ollama','openai','gemini'):raise ValueError('Preferência da conversa inválida.')
                local=validar_config(json.loads(row['config'])) if provider=='ollama' else None
        return {'provedor':provider,'modelo':model,'local':local,'escopo':scope}

    def _config(self,h=None,cid=None):
        selection=self._selecao(h,cid)
        local=self._ia_preferencias.ler()['ollama']
        providers={p:{'modelo':configuracao(p)[1],'configurada':bool(configuracao(p)[0]),'local':False} for p in ['gemini','openai']}
        providers['ollama']={**local,'configurada':True,'local':True}
        return {**selection,'padrao':self._selecao()['provedor'],'provedores':providers}

    def _material(self,b,m,cid):
        # DTO explicito: nenhum caminho local, hash ou chave sai para o navegador.
        campos=['id','nome','tipo','tamanho','url','estado','aviso','metodo','materia','assunto','etiquetas','origem_id','origem_titulo','criado']
        item={k:m[k] for k in campos}
        item['estado_rotulo']=ESTADOS[m['estado']]
        item['cadernos']=[x['id'] for x in b.cadernos_material(m['id'])]
        anexo=next((a for a in b.anexos(cid) if a['id']==m['id']),None)
        item['anexado']=anexo is not None
        item['selecionado']=bool(anexo and anexo['selecionado'])
        item['processando']=m['id'] in self._processando
        return item

    def executar(self,operacao,dados):
        from .estudo import OPERACOES
        operacoes={'estado':self._estado,'navegar':self._navegar,'chat_criar':self._chat_criar,
            'chat_acao':self._chat_acao,'rascunho':self._rascunho,'caderno_salvar':self._caderno_salvar,
            'caderno_acao':self._caderno_acao,'materiais':self._materiais,'link':self._link,
            'material_acao':self._material_acao,'material_salvar':self._material_salvar,
            'material_detalhe':self._material_detalhe,'previa':self._previa,'enviar':self._enviar,
            'configurar':self._configurar,'preferencias':self._salvar_preferencias,
            'ollama_diagnostico':self._ollama_diagnostico,'ollama_iniciar':self._ollama_iniciar,'ia_cancelar':self._ia_cancelar,
            'ia_repetir':self._ia_repetir,'semantica_status':self._semantica_status,
            'semantica_indexar':self._semantica_indexar,'semantica_cancelar':self._semantica_cancelar,
            'semantica_ativar':self._semantica_ativar}
        operacoes.update({op:(lambda d, op=op:self._estudo.executar(op,d)) for op in OPERACOES})
        from .calculos import OPERACOES as MATH_OPS
        operacoes.update({op:(lambda d, op=op:self._calculos.executar(op,d)) for op in MATH_OPS})
        if not isinstance(operacao,str) or operacao not in operacoes:raise ValueError('Operacao nao permitida.')
        if not isinstance(dados,dict) or len(dados)>15:raise ValueError('Parametros invalidos.')
        with self._lock:
            if self._fechado:raise ValueError('Aplicativo encerrado.')
            return operacoes[operacao](dados)

    def _estado(self,d):
        busca=texto(d.get('busca',''),300)
        with self._banco() as (h,c,b):
            nav=c.navegacao(); cid=nav['conversa_id']
            chat=h.obter(cid) if cid else None
            return {'revisao':self._revisao,'cadernos':c.listar(None),'navegacao':nav,
                'conversas':h.listar(busca,bool(nav['arquivados']),nav['caderno_id']),
                'conversa':chat,'mensagens':h.mensagens(cid),
                'calculos':self._calculos.listar(h,cid),
                'anexos':[self._material(b,m,cid) for m in b.anexos(cid)],
                'config':self._config(h,cid),'preferencias':self._preferencias(),
                'ocupado':self._ocupado(),'tarefas':list(self._tarefas.values())[-20:],
                'estudo':self._estudo_navegacao(h)}

    def _estudo_navegacao(self,h):
        from .atividades import Atividades
        return Atividades(h).navegacao()

    def _navegar(self,d):
        self._livre()
        with self._banco() as (h,c,b):
            caderno=ident(d.get('caderno'),True)
            if caderno:c.obter(caderno)
            cid=ident(d.get('conversa'),True)
            arquivo=booleano(d.get('arquivadas',False))
            if cid:
                chat=h.obter(cid);caderno=chat['caderno_id'];arquivo=bool(chat['arquivada'])
            elif not booleano(d.get('vazio',False)):
                chats=h.listar(arquivadas=arquivo,caderno=caderno)
                cid=chats[0]['id'] if chats else None
            c.salvar_navegacao(caderno,cid,arquivo)
        self._revisao+=1
        return self._estado({})

    def _chat_criar(self,d):
        self._livre()
        with self._banco() as (h,c,b):
            destino=ident(d.get('caderno'),True)
            cid=h.criar(destino);c.salvar_navegacao(destino,cid)
        self._revisao+=1
        return self._estado({})

    def _chat_acao(self,d):
        self._livre();cid=ident(d.get('id'));acao=d.get('acao')
        with self._banco() as (h,c,b):
            chat=h.obter(cid);nav=c.navegacao()
            if acao=='renomear':h.renomear(cid,texto(d.get('titulo'),100,False))
            elif acao=='fixar':h.fixar(cid,booleano(d.get('valor')))
            elif acao=='arquivar':h.arquivar(cid,booleano(d.get('valor')))
            elif acao=='mover':
                destino=ident(d.get('destino'),True);c.mover_conversa(cid,destino)
                c.salvar_navegacao(destino,cid,bool(chat['arquivada']))
            elif acao=='excluir':
                if d.get('confirmado') is not True:raise ValueError('Confirme a exclusao do chat.')
                h.excluir(cid)
            else:raise ValueError('Acao de chat invalida.')
            if acao in ['arquivar','excluir'] and nav['conversa_id']==cid:
                chats=h.listar(arquivadas=bool(nav['arquivados']),caderno=nav['caderno_id'])
                c.salvar_navegacao(nav['caderno_id'],chats[0]['id'] if chats else None,bool(nav['arquivados']))
        self._revisao+=1
        return self._estado({})

    def _rascunho(self,d):
        cid=ident(d.get('id'));conteudo=texto(d.get('texto'),30000)
        with self._banco() as (h,c,b):
            self._editavel(h,c,cid);h.rascunho(cid,conteudo)
        return None

    def _caderno_salvar(self,d):
        self._livre();cid=ident(d.get('id'),True)
        permitidos=['nome','descricao','objetivo','nivel','assuntos','preferencia','orientacao']
        campos={k:texto(d[k],1500) for k in permitidos if k in d}
        if 'nome' not in campos:raise ValueError('Informe o nome do caderno.')
        with self._banco() as (h,c,b):
            if cid:c.editar(cid,**campos)
            else:
                cid=c.criar(**campos);c.salvar_navegacao(cid,None)
        self._revisao+=1
        return self._estado({})

    def _caderno_acao(self,d):
        self._livre();cid=ident(d.get('id'));acao=d.get('acao')
        with self._banco() as (h,c,b):
            c.obter(cid)
            if acao=='arquivar':c.arquivar(cid,booleano(d.get('valor')))
            elif acao=='ordenar':
                passo=d.get('passo')
                if type(passo) is not int:raise ValueError('Ordem invalida.')
                c.ordenar(cid,passo)
            elif acao=='excluir':
                if d.get('confirmado') is not True:raise ValueError('Confirme a exclusao do caderno.')
                c.excluir(cid)
            else:raise ValueError('Acao de caderno invalida.')
        self._revisao+=1
        return self._estado({})

    def _materiais(self,d):
        caderno=d.get('caderno','todos')
        if caderno!='todos':ident(caderno,True)
        pagina=d.get('pagina',0);dias=d.get('dias',0)
        if type(pagina) is not int or not 0<=pagina<=100000 or dias not in [0,7,30,90]:raise ValueError('Filtro invalido.')
        with self._banco() as (h,c,b):
            cid=c.navegacao()['conversa_id']
            modo=d.get('modo','texto')
            if modo not in ('texto','hibrida'):raise ValueError('Modo de busca inválido.')
            busca=texto(d.get('busca',''),300)
            registros=[] if booleano(d.get('so_chat',False)) and not cid else b.listar(
                busca if modo=='texto' else '',texto(d.get('tipo',''),20),texto(d.get('materia',''),100),
                dias,cid if d.get('so_chat') else None,TODOS_CADERNOS if caderno=='todos' else caderno)
            report={}
            ocorrencias={}
            if modo=='hibrida' and busca.strip():
                from .semantica import IndiceSemantico
                hits=IndiceSemantico(h).candidatos([m['id'] for m in registros],busca,report)
                for hit in hits:
                    ocorrencias.setdefault(hit['material_id'],[]).append({k:hit[k] for k in ('pagina','texto','selecao')})
                nomes=b.listar(busca,texto(d.get('tipo',''),20),texto(d.get('materia',''),100),dias,
                    cid if d.get('so_chat') else None,TODOS_CADERNOS if caderno=='todos' else caderno)
                ranked=list(ocorrencias)+[m['id'] for m in nomes if m['id'] not in ocorrencias]
                byid={m['id']:m for m in registros}
                registros=[byid[mid] for mid in ranked if mid in byid]
            pagina=min(pagina,max(0,(len(registros)-1)//30))
            return {'itens':[{**self._material(b,m,cid),'ocorrencias':ocorrencias.get(m['id'],[])[:2]} for m in registros[pagina*30:(pagina+1)*30]],
                    'total':len(registros),'pagina':pagina,'materias':b.materias(),'recuperacao':report}

    def _garantir_chat(self,h,c):
        nav=c.navegacao();cid=nav['conversa_id']
        if not cid:
            cid=h.criar(nav['caderno_id']);c.salvar_navegacao(nav['caderno_id'],cid)
        self._editavel(h,c,cid)
        return cid

    def importar(self,caminhos):
        # Somente o dialogo nativo chama este metodo; nao e exposto na ponte.
        with self._lock:
            self._livre();erros=[]
            with self._banco() as (h,c,b):
                cid=self._garantir_chat(h,c)
                for caminho in caminhos[:20]:
                    try:
                        mid,novo=b.adicionar_arquivo(caminho,cid)
                        if novo:self._agendar(mid)
                    except (OSError,ValueError):erros.append('Um arquivo nao pode ser importado. Confira o formato e o limite de 20 MiB.')
            self._revisao+=1
            return {'estado':self._estado({}),'avisos':list(dict.fromkeys(erros))}

    def _link(self,d):
        self._livre();url=normalizar_url(texto(d.get('url'),2000,False))
        with self._banco() as (h,c,b):
            cid=self._garantir_chat(h,c);mid,novo=b.adicionar_link(url,cid)
            if novo:self._agendar(mid)
        self._revisao+=1
        return self._estado({})

    def _agendar(self,mid):
        if mid in self._processando:return
        self._processando.add(mid)
        with self._banco() as (h,c,b):
            with h.db:h.db.execute("UPDATE materiais SET estado='pendente',aviso='Aguardando processamento local.' WHERE id=?",(mid,))
        self._executor.submit(self._processar,mid)

    def _processar(self,mid):
        try:
            subprocess.run([sys.executable,'-m','tutor_calculo.processamento',str(self.caminho),mid],
                cwd=Path(__file__).resolve().parents[1],capture_output=True,timeout=150,check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        except Exception:
            with self._banco() as (h,c,b):
                b.salvar_extracao(mid,Extracao([],'erro','Falha ou limite de 150 segundos. Tente reprocessar.'))
        finally:
            with self._lock:self._processando.discard(mid);self._revisao+=1

    def _material_acao(self,d):
        self._livre();mid=ident(d.get('id'));acao=d.get('acao')
        with self._banco() as (h,c,b):
            m=b.obter(mid)
            if acao in ['selecionar','reutilizar','desvincular']:
                cid=self._garantir_chat(h,c)
                if acao=='selecionar':
                    if m['estado'] not in ['pronto','parcial']:raise ValueError('Aguarde texto interpretavel antes de selecionar.')
                    b.vincular(mid,cid,booleano(d.get('valor')))
                elif acao=='reutilizar':b.vincular(mid,cid)
                else:b.desvincular(mid,cid)
            elif acao=='reprocessar':self._agendar(mid)
            elif acao=='excluir':
                if mid in self._processando:raise ValueError('Aguarde o processamento para excluir.')
                if d.get('confirmado') is not True:raise ValueError('Confirme a exclusao do material.')
                b.excluir(mid)
            else:raise ValueError('Acao de material invalida.')
        self._revisao+=1
        return self._estado({})

    def _material_salvar(self,d):
        self._livre();mid=ident(d.get('id'));ids=d.get('cadernos',[])
        if not isinstance(ids,list) or len(ids)>100:raise ValueError('Associacoes invalidas.')
        for cid in ids:ident(cid)
        with self._banco() as (h,c,b):
            b.metadados(mid,texto(d.get('nome'),240,False),texto(d.get('materia',''),100),
                texto(d.get('assunto',''),200),texto(d.get('etiquetas',''),500),ids)
        self._revisao+=1
        return self._estado({})

    def _material_detalhe(self,d):
        mid=ident(d.get('id'));pagina=d.get('pagina',1)
        if type(pagina) is not int or not 1<=pagina<=100000:raise ValueError('Pagina invalida.')
        with self._banco() as (h,c,b):
            m=b.obter(mid);paginas=b.paginas(mid)
            trecho=next((p['texto'] for p in paginas if p['numero']==pagina),'')
            retorno={'material':self._material(b,m,c.navegacao()['conversa_id']),
                'paginas':[p['numero'] for p in paginas],'texto':trecho,'imagem':None,'aviso_previa':''}
            try:
                original=b.caminho_original(mid)
                if m['tipo']=='pdf':
                    from .extracao import imagem_pdf
                    img=imagem_pdf(original,pagina)
                elif m['tipo']=='imagem':
                    from PIL import Image
                    with Image.open(original) as fonte:
                        if fonte.width*fonte.height>40_000_000:raise ValueError('Imagem grande')
                        img=fonte.copy()
                else:return retorno
                img.thumbnail((1000,1000));buf=io.BytesIO();img.save(buf,format='PNG')
                retorno['imagem']='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
            except Exception:retorno['aviso_previa']='Previa original indisponivel. Confira o arquivo ou pagina.'
            return retorno

    def _fontes(self,h,b,cid,pergunta,detalhes=None):
        if not any(m['selecionado'] for m in b.anexos(cid)):return None
        if len(pergunta.split())<4:
            anteriores=[m['texto'] for m in h.mensagens(cid) if m['papel']=='user']
            if anteriores:pergunta+=' '+anteriores[-1][:400]
        from .recuperacao import recuperar_chat
        return recuperar_chat(b,cid,pergunta,detalhes)

    def _previa(self,d):
        cid=ident(d.get('id'),True);pergunta=texto(d.get('texto',''),30000)
        with self._banco() as (h,c,b):
            chat=h.obter(cid) if cid else None
            bid=chat['caderno_id'] if chat else c.navegacao()['caderno_id']
            caderno=c.obter(bid) if bid else None
            selection=self._selecao(h,cid)
            mode=d.get('modo','Resolver')
            calc=mode=='Resolver' and usa_analisador(pergunta)
            if mode=='Resolver com IA':mode='Resolver'
            recuperacao={}
            p={'pedagogia':'','historico':[],'fontes':None,'instrucoes':'','orcamento':None} if calc else preparar_consulta(
                pergunta or '(mensagem vazia)',modo=mode,historico=h.mensagens(cid),fontes=self._fontes(h,b,cid,pergunta,recuperacao),
                caderno=caderno,provedor=selection['provedor'],local=selection['local'])
            return {**selection,'pedagogia':p['pedagogia'],'mensagem':pergunta,'historico':p['historico'],
                'fontes':p['fontes'],'recuperacao':recuperacao,'instrucoes':p['instrucoes'],'orcamento':p['orcamento'],
                'destino':'Cálculo simbólico neste computador, sem consulta à IA' if calc else 'Somente Ollama neste computador' if selection['local'] else 'Provedor online',
                'originais_enviados':False}

    def _enviar(self,d):
        cid=ident(d.get('id'));pergunta=texto(d.get('texto'),30000,False)
        modo=d.get('modo','Resolver com IA')
        if modo not in ['Resolver','Resolver com IA','Explicar','Corrigir']:raise ValueError('Modo invalido.')
        tid=ident(d.get('requisicao',str(uuid4())))
        with self._banco() as (h,c,b):
            existing=h.db.execute('SELECT * FROM consultas_ia WHERE id=?',(tid,)).fetchone()
            if existing:
                snap=json.loads(existing['snapshot'])
                if existing['conversa_id']!=cid or snap['pergunta']!=pergunta or snap['modo']!=modo:raise ValueError('ID de consulta reutilizado com dados diferentes.')
                return {'tarefa':tid}
            self._livre()
            chat=self._editavel(h,c,cid);historico=h.mensagens(cid);recuperacao={};fontes=self._fontes(h,b,cid,pergunta,recuperacao)
            if modo=='Resolver' and fontes is not None:raise ValueError('Escolha um modo de IA para consultar materiais.')
            caderno=c.obter(chat['caderno_id']) if chat['caderno_id'] else None
            selection=self._selecao(h,cid)
            calculo_local=modo=='Resolver' and usa_analisador(pergunta)
            prepared=None if calculo_local else preparar_consulta(pergunta,'Resolver' if modo in ('Resolver com IA','Resolver') else modo,
                historico,fontes,caderno,selection['provedor'],selection['local'])
            snapshot={'recuperacao':recuperacao,'pergunta':pergunta,'modo':modo,'historico':historico,'fontes':fontes,'caderno':caderno,
                      'selecao':selection,'preparada':prepared,'calculo_local':calculo_local}
            with h.db:
                uid=h.db.execute("INSERT INTO mensagens(conversa_id,papel,texto,estado) VALUES(?,'user',?,'ok')",(cid,pergunta)).lastrowid
                if not historico:h.db.execute('UPDATE conversas SET titulo=? WHERE id=?',(pergunta.splitlines()[0][:80],cid))
                h.db.execute("UPDATE conversas SET rascunho='',atualizado=CURRENT_TIMESTAMP WHERE id=?",(cid,))
                h.db.execute("INSERT INTO consultas_ia(id,conversa_id,usuario_id,snapshot,estado) VALUES(?,?,?,?,'executando')",(tid,cid,uid,json.dumps(snapshot,ensure_ascii=False)))
        self._iniciar_consulta(tid,cid,snapshot)
        return {'tarefa':tid}

    def _iniciar_consulta(self,tid,cid,snapshot):
        if len(self._tarefas)>=20:
            for key in [k for k,v in self._tarefas.items() if v['estado']!='executando'][:-18]:
                self._tarefas.pop(key);self._cancelamentos.pop(key,None)
        self._cancelamentos[tid]=Cancelamento()
        self._tarefas[tid]={'id':tid,'tipo':'ia','estado':'executando','conversa':cid,'parcial':'',
            'cancelavel':snapshot['selecao']['provedor']=='ollama' and not snapshot.get('calculo_local'),
            'provedor':snapshot['selecao']['provedor'],'modelo':snapshot['selecao']['modelo']}
        self._revisao+=1
        self._executor.submit(self._consultar,tid,cid,snapshot)

    def _consultar(self,tid,cid,snapshot):
        estado='ok';error='';partial='';last_write=0;metrics={}
        pergunta,modo,historico,fontes,caderno=[snapshot[k] for k in ('pergunta','modo','historico','fontes','caderno')]
        selection=snapshot['selecao'];token=self._cancelamentos[tid]
        def trecho(value):
            nonlocal partial,last_write
            partial+=value
            with self._lock:
                self._tarefas[tid]['parcial']=partial
                if time.monotonic()-last_write>=.3:
                    with self._banco() as (h,c,b):
                        with h.db:h.db.execute('UPDATE consultas_ia SET parcial=? WHERE id=?',(partial,tid))
                    last_write=time.monotonic();self._revisao+=1
        try:
            token.verificar()
            resposta=resolver(pergunta,caderno=caderno,historico=historico,provedor=selection['provedor'],modelo=selection['modelo'],
                local=selection['local'],cancelar=token,trecho=trecho,metricas=metrics.update,preparada=snapshot['preparada']) if modo=='Resolver' else perguntar(
                pergunta,modo='Resolver' if modo=='Resolver com IA' else modo,historico=historico,fontes=fontes,caderno=caderno,
                provedor=selection['provedor'],modelo=selection['modelo'],local=selection['local'],cancelar=token,
                trecho=trecho,metricas=metrics.update,preparada=snapshot['preparada'])
            token.verificar()
        except ConsultaCancelada as exc:estado='cancelada';error=str(exc)
        except RespostaIncompleta as exc:estado='incompleta';error=str(exc)
        except (ValueError,RuntimeError,ImportError) as exc:estado='erro';error=str(exc)
        except Exception:estado='erro';error='Falha inesperada na consulta. Revise o enunciado e tente novamente.'
        if estado!='ok':resposta=(partial+'\n\n' if partial else '')+error
        with self._lock:
            if token.evento.is_set() and estado=='ok':
                estado='cancelada';error='Consulta cancelada antes de concluir.';resposta=(partial+'\n\n' if partial else '')+error
            with self._banco() as (h,c,b):
                with h.db:
                    rid=h.db.execute("INSERT INTO mensagens(conversa_id,papel,texto,estado,provedor,modelo) VALUES(?,'assistant',?,?,?,?)",(cid,resposta,estado,selection['provedor'] if not snapshot.get('calculo_local') else 'local/IA',selection['modelo'] if not snapshot.get('calculo_local') else 'SymPy')).lastrowid
                    h.db.execute('UPDATE consultas_ia SET resposta_id=?,estado=?,parcial=?,erro=?,metricas=? WHERE id=?',(rid,estado,partial,error,json.dumps(metrics),tid))
                    if estado!='ok' and not h.obter(cid)['rascunho']:h.db.execute('UPDATE conversas SET rascunho=? WHERE id=?',(pergunta,cid))
                    h.db.execute('UPDATE conversas SET atualizado=CURRENT_TIMESTAMP WHERE id=?',(cid,))
            self._tarefas[tid].update(estado='concluida' if estado=='ok' else estado,metricas=metrics,parcial='')
            self._revisao+=1

    def _recuperar_consultas(self):
        with self._banco() as (h,c,b):
            for row in h.db.execute("SELECT * FROM consultas_ia WHERE estado='executando'").fetchall():
                snapshot=json.loads(row['snapshot']);sel=snapshot['selecao']
                message='Consulta interrompida ao encerrar o aplicativo; resposta incompleta. Confira e tente novamente.'
                with h.db:
                    rid=h.db.execute("INSERT INTO mensagens(conversa_id,papel,texto,estado,provedor,modelo) VALUES(?,'assistant',?,'incompleta',?,?)",(row['conversa_id'],(row['parcial']+'\n\n' if row['parcial'] else '')+message,sel['provedor'],sel['modelo'])).lastrowid
                    h.db.execute("UPDATE consultas_ia SET estado='incompleta',resposta_id=?,erro=? WHERE id=?",(rid,message,row['id']))
                    h.db.execute("UPDATE conversas SET rascunho=CASE WHEN rascunho='' THEN ? ELSE rascunho END WHERE id=?",(snapshot['pergunta'],row['conversa_id']))

    def _ia_cancelar(self,d):
        tid=ident(d.get('id'));task=self._tarefas.get(tid)
        if not task:raise ValueError('Consulta não encontrada.')
        if task['estado']=='executando':
            if not task.get('cancelavel'):raise ValueError('Este provedor não oferece cancelamento nesta interface.')
            self._cancelamentos[tid].cancelar();task['cancelando']=True
        return {'id':tid,'estado':task['estado']}

    def _ia_repetir(self,d):
        old=ident(d.get('id'));tid=ident(d.get('requisicao',str(uuid4())))
        with self._banco() as (h,c,b):
            row=h.db.execute('SELECT * FROM consultas_ia WHERE id=?',(old,)).fetchone()
            if not row or row['estado'] not in ('erro','cancelada','incompleta'):raise ValueError('Repita somente uma consulta não concluída.')
            cid=row['conversa_id'];self._editavel(h,c,cid);snap=json.loads(row['snapshot'])
            selection=self._selecao(h,cid)
            if selection!=snap['selecao']:raise ValueError('A configuração mudou. Confira uma nova prévia e envie a pergunta novamente.')
            # Material removido/desmarcado não pode voltar a ser enviado via repetição.
            selected={m['id'] for m in b.anexos(cid) if m['selecionado']}
            if any(f['material_id'] not in selected for f in snap['fontes'] or []):raise ValueError('A seleção documental mudou. Confira uma nova prévia.')
            existing=h.db.execute('SELECT * FROM consultas_ia WHERE id=?',(tid,)).fetchone()
            if existing:
                if existing['conversa_id']!=cid or existing['usuario_id']!=row['usuario_id']:raise ValueError('ID de consulta inválido.')
                return {'tarefa':tid}
            self._livre()
            with h.db:
                h.db.execute("INSERT INTO consultas_ia(id,conversa_id,usuario_id,snapshot,estado) VALUES(?,?,?,?,'executando')",(tid,cid,row['usuario_id'],row['snapshot']))
                h.db.execute("UPDATE conversas SET rascunho='' WHERE id=? AND rascunho=?",(cid,snap['pergunta']))
        self._iniciar_consulta(tid,cid,snap)
        return {'tarefa':tid}

    def _configurar(self,d):
        self._livre();provedor=d.get('provedor')
        if provedor not in ['gemini','openai','ollama']:raise ValueError('Provedor invalido.')
        scope=d.get('escopo','padrao')
        if scope not in ('padrao','chat','herdar'):raise ValueError('Escopo inválido.')
        model=texto(d.get('modelo',''),100,scope=='herdar')
        local=validar_config({'modelo':model,'url':d.get('url','http://127.0.0.1:11434'),
            'contexto':d.get('contexto',4096),'timeout':d.get('timeout',180)}) if provedor=='ollama' and scope!='herdar' else None
        with self._banco() as (h,c,b):
            cid=c.navegacao()['conversa_id']
            if scope in ('chat','herdar'):
                if not cid:raise ValueError('Crie ou abra uma conversa para configurar seu provedor.')
                self._editavel(h,c,cid)
            if scope=='herdar':
                with h.db:h.db.execute('DELETE FROM chat_ia WHERE conversa_id=?',(cid,))
            else:
                if provedor!='ollama':
                    args=(texto(d.get('chave',''),500),model,provedor)
                    if scope=='padrao':salvar_configuracao(*args)
                    else:salvar_configuracao(*args,ativar=False)
                if scope=='padrao':self._ia_preferencias.salvar(provedor,local)
                else:
                    with h.db:h.db.execute('INSERT OR REPLACE INTO chat_ia(conversa_id,provedor,modelo,config) VALUES(?,?,?,?)',(cid,provedor,model,json.dumps(local or {})))
        self._revisao+=1
        with self._banco() as (h,c,b):return self._config(h,c.navegacao()['conversa_id'])

    def _ollama_diagnostico(self,d):
        self._livre()
        conf=validar_config({k:d.get(k,v) for k,v in self._ia_preferencias.ler()['ollama'].items()})
        return Ollama(conf).diagnostico()

    def _ollama_iniciar(self,d):
        self._livre()
        conf=validar_config({k:d.get(k,v) for k,v in self._ia_preferencias.ler()['ollama'].items()})
        client=Ollama(conf)
        try:client.metadados('version',timeout=1);return {'iniciado':False}
        except RuntimeError:pass
        base=self.caminho.parent/'ia-local'
        try:runtime=Path((base/'runtime-path.txt').read_text().strip()).resolve(strict=True)
        except OSError:raise ValueError('Runtime do piloto ausente. Inicie o aplicativo Ollama instalado neste computador; não há download automático.') from None
        if (not runtime.is_relative_to((base/'runtimes').resolve()) or runtime.name!='ollama'
                or runtime.parent.name!='bin' or not os.access(runtime,os.X_OK)):
            raise ValueError('Caminho do runtime do piloto inválido.')
        env={**os.environ,'OLLAMA_HOST':conf['url'].removeprefix('http://'),
            'OLLAMA_MODELS':str(base/'models'),'OLLAMA_NO_CLOUD':'1','OLLAMA_NUM_PARALLEL':'1',
            'OLLAMA_MAX_LOADED_MODELS':'1','OLLAMA_CONTEXT_LENGTH':str(conf['contexto']),'OLLAMA_KEEP_ALIVE':'2m'}
        log=base/'servidor-integrado.log'
        with open(os.open(log,os.O_CREAT|os.O_APPEND|os.O_WRONLY,0o600),'ab') as output:
            process=subprocess.Popen([str(runtime),'serve'],env=env,stdout=output,stderr=output,
                start_new_session=os.name!='nt',creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        prazo=time.monotonic()+8
        while time.monotonic()<prazo:
            if process.poll() is not None:raise RuntimeError('O runtime não iniciou. Confira a instalação do piloto e a porta local.')
            try:client.metadados('version',timeout=1);return {'iniciado':True}
            except RuntimeError:time.sleep(.2)
        raise RuntimeError('O runtime está iniciando. Aguarde e use Testar conexão novamente.')

    def _semantica_status(self,d):
        from .semantica import IndiceSemantico
        with self._banco() as (h,c,b):return IndiceSemantico(h).status()

    def _semantica_ativar(self,d):
        self._livre();value=booleano(d.get('valor'))
        with self._banco() as (h,c,b):
            with h.db:h.db.execute('UPDATE semantica_config SET habilitada=? WHERE id=1',(int(value),))
        self._revisao+=1
        return self._semantica_status({})

    def _semantica_indexar(self,d):
        from .semantica import IndiceSemantico
        self._livre()
        if self._processando:raise ValueError('Aguarde a extração dos materiais antes de indexar.')
        if d.get('confirmado') is not True:raise ValueError('Confirme a indexação local dos textos da biblioteca.')
        with self._banco() as (h,c,b):
            index=IndiceSemantico(h)
            url=texto(d.get('url',index.config()['url']),200,False)
            tid=index.iniciar(url)
        self._indice_cancelamento=Cancelamento()
        self._tarefas[tid]={'id':tid,'tipo':'indice','estado':'executando','conversa':None,'feitos':0,'total':0}
        self._revisao+=1
        self._executor.submit(self._indexar_semantica,tid,self._indice_cancelamento)
        return {'tarefa':tid}

    def _indexar_semantica(self,tid,token):
        from .semantica import IndiceSemantico
        def progresso(done,total):
            with self._lock:
                self._tarefas[tid].update(feitos=done,total=total);self._revisao+=1
        estado='concluido';error=''
        try:
            with self._banco() as (h,c,b):IndiceSemantico(h).indexar(tid,token,progresso)
        except ConsultaCancelada:estado='cancelado';error='Indexação cancelada. A preparação foi preservada; use Indexar / retomar.'
        except (ValueError,RuntimeError) as exc:estado='erro';error=str(exc)
        except Exception:estado='erro';error='Falha na indexação local. A busca textual continua disponível.'
        with self._lock:
            with self._banco() as (h,c,b):
                with h.db:h.db.execute('UPDATE semantica_trabalho SET estado=?,erro=?,atualizado=CURRENT_TIMESTAMP WHERE execucao=?',(estado,error,tid))
            self._tarefas[tid].update(estado=estado,erro=error);self._revisao+=1

    def _semantica_cancelar(self,d):
        if self._indice_cancelamento:self._indice_cancelamento.cancelar()
        return self._semantica_status({})

    def _salvar_preferencias(self,d):
        if d.get('tema') not in ['claro','escuro']:raise ValueError('Tema invalido.')
        dados={'tema':d['tema'],'recolhida':booleano(d.get('recolhida',False))}
        destino=self.caminho.parent/'interface.json';tmp=destino.with_suffix('.tmp')
        tmp.write_text(json.dumps(dados));tmp.chmod(0o600);os.replace(tmp,destino)
        return dados

    def fechar(self):
        with self._lock:
            self._fechado=True
            for token in self._cancelamentos.values():token.cancelar()
            if self._indice_cancelamento:self._indice_cancelamento.cancelar()
        # Filas interrompidas e processos encerrados são recuperados do SQLite.
        self._executor.shutdown(wait=False,cancel_futures=True)
