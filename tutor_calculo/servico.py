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

from .armazenamento import Historico, TODOS_CADERNOS, caminho_banco
from .cadernos import Cadernos, contexto_pedagogico
from .materiais import Biblioteca, Extracao, ESTADOS
from .ia import configuracao, limitar_contexto, perguntar, provedor_ativo, salvar_configuracao
from .app import resolver
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
        self._processando=set()
        self._revisao=0
        self._fechado=False
        with self._banco() as (h,c,b):
            Biblioteca(h,recuperar=True)
            nav=c.navegacao()
            if nav['conversa_id'] is None:
                chats=h.listar(caderno=nav['caderno_id'])
                if chats:c.salvar_navegacao(nav['caderno_id'],chats[0]['id'])

    @contextmanager
    def _banco(self):
        h=Historico(self.caminho)
        try:yield h,Cadernos(h),Biblioteca(h)
        finally:h.fechar()

    def _ocupado(self):
        return any(t['tipo']=='ia' and t['estado']=='executando' for t in self._tarefas.values())

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

    def _config(self):
        return {'provedor':provedor_ativo(),'provedores':{
            p:{'modelo':configuracao(p)[1],'configurada':bool(configuracao(p)[0])} for p in ['gemini','openai']}}

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
        operacoes={'estado':self._estado,'navegar':self._navegar,'chat_criar':self._chat_criar,
            'chat_acao':self._chat_acao,'rascunho':self._rascunho,'caderno_salvar':self._caderno_salvar,
            'caderno_acao':self._caderno_acao,'materiais':self._materiais,'link':self._link,
            'material_acao':self._material_acao,'material_salvar':self._material_salvar,
            'material_detalhe':self._material_detalhe,'previa':self._previa,'enviar':self._enviar,
            'configurar':self._configurar,'preferencias':self._salvar_preferencias}
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
                'anexos':[self._material(b,m,cid) for m in b.anexos(cid)],
                'config':self._config(),'preferencias':self._preferencias(),
                'ocupado':self._ocupado(),'tarefas':list(self._tarefas.values())[-20:]}

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
            registros=[] if booleano(d.get('so_chat',False)) and not cid else b.listar(
                texto(d.get('busca',''),300),texto(d.get('tipo',''),20),texto(d.get('materia',''),100),
                dias,cid if d.get('so_chat') else None,TODOS_CADERNOS if caderno=='todos' else caderno)
            pagina=min(pagina,max(0,(len(registros)-1)//30))
            return {'itens':[self._material(b,m,cid) for m in registros[pagina*30:(pagina+1)*30]],
                    'total':len(registros),'pagina':pagina,'materias':b.materias()}

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

    def _fontes(self,h,b,cid,pergunta):
        if not any(m['selecionado'] for m in b.anexos(cid)):return None
        if len(pergunta.split())<4:
            anteriores=[m['texto'] for m in h.mensagens(cid) if m['papel']=='user']
            if anteriores:pergunta+=' '+anteriores[-1][:400]
        return b.recuperar(cid,pergunta)

    def _previa(self,d):
        cid=ident(d.get('id'),True);pergunta=texto(d.get('texto',''),30000)
        with self._banco() as (h,c,b):
            chat=h.obter(cid) if cid else None
            bid=chat['caderno_id'] if chat else c.navegacao()['caderno_id']
            caderno=c.obter(bid) if bid else None
            return {'provedor':provedor_ativo(),'modelo':configuracao()[1],
                'pedagogia':contexto_pedagogico(caderno),'mensagem':pergunta,
                'historico':limitar_contexto(h.mensagens(cid)),
                'fontes':self._fontes(h,b,cid,pergunta),'originais_enviados':False}

    def _enviar(self,d):
        self._livre();cid=ident(d.get('id'));pergunta=texto(d.get('texto'),30000,False)
        modo=d.get('modo','Resolver com IA')
        if modo not in ['Resolver','Resolver com IA','Explicar','Corrigir']:raise ValueError('Modo invalido.')
        with self._banco() as (h,c,b):
            chat=self._editavel(h,c,cid);historico=h.mensagens(cid);fontes=self._fontes(h,b,cid,pergunta)
            if modo=='Resolver' and fontes is not None:raise ValueError('Escolha um modo de IA para consultar materiais.')
            caderno=c.obter(chat['caderno_id']) if chat['caderno_id'] else None
            provedor=provedor_ativo();modelo=configuracao()[1]
            h.adicionar(cid,'user',pergunta)
            if not historico:h.renomear(cid,pergunta.splitlines()[0][:80])
            h.rascunho(cid,'')
        if len(self._tarefas)>=20:
            antigos=[k for k,v in self._tarefas.items() if v['estado']!='executando']
            for k in antigos[:-18]:self._tarefas.pop(k)
        tid=str(uuid4());self._tarefas[tid]={'id':tid,'tipo':'ia','estado':'executando','conversa':cid}
        self._revisao+=1
        self._executor.submit(self._consultar,tid,cid,pergunta,modo,historico,fontes,caderno,provedor,modelo)
        return {'tarefa':tid}

    def _consultar(self,tid,cid,pergunta,modo,historico,fontes,caderno,provedor,modelo):
        estado='ok'
        try:
            resposta=resolver(pergunta,caderno=caderno,historico=historico) if modo=='Resolver' else perguntar(
                pergunta,modo='Resolver' if modo=='Resolver com IA' else modo,historico=historico,fontes=fontes,caderno=caderno)
        except (ValueError,RuntimeError,ImportError) as exc:estado='erro';resposta=str(exc)
        except Exception:estado='erro';resposta='Falha inesperada na consulta. Revise o enunciado e tente novamente.'
        with self._lock:
            with self._banco() as (h,c,b):
                h.adicionar(cid,'assistant',resposta,estado,provedor if modo!='Resolver' else 'local/IA',modelo)
                if estado=='erro' and not h.obter(cid)['rascunho']:h.rascunho(cid,pergunta)
            self._tarefas[tid]['estado']='erro' if estado=='erro' else 'concluida'
            self._revisao+=1

    def _configurar(self,d):
        self._livre();provedor=d.get('provedor')
        if provedor not in ['gemini','openai']:raise ValueError('Provedor invalido.')
        salvar_configuracao(texto(d.get('chave',''),500),texto(d.get('modelo'),100,False),provedor)
        self._revisao+=1
        return self._config()

    def _salvar_preferencias(self,d):
        if d.get('tema') not in ['claro','escuro']:raise ValueError('Tema invalido.')
        dados={'tema':d['tema'],'recolhida':booleano(d.get('recolhida',False))}
        destino=self.caminho.parent/'interface.json';tmp=destino.with_suffix('.tmp')
        tmp.write_text(json.dumps(dados));tmp.chmod(0o600);os.replace(tmp,destino)
        return dados

    def fechar(self):
        with self._lock:self._fechado=True
        # Tarefas ativas salvam sua resposta com conexao propria; filas interrompidas sao recuperaveis.
        self._executor.shutdown(wait=False,cancel_futures=True)
