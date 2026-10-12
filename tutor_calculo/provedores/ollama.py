"""API nativa de Ollama em loopback; sem proxies, downloads ou fallback."""
import http.client
import json
import re
import socket
import time
from threading import Timer
from urllib.parse import urlsplit

from .contratos import Cancelamento, RespostaIncompleta, ErroLocal

PADRAO = {'url': 'http://127.0.0.1:11434', 'modelo': 'qwen3.5:4b-q4_K_M', 'contexto': 4096, 'timeout': 180, 'perfil': 'rapido'}


def validar_modelo(modelo):
    if (not isinstance(modelo, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./:-]{0,99}', modelo)
            or '..' in modelo or 'cloud' in modelo.lower().split(':')[-1]
            or modelo.lower().endswith('-cloud')):
        raise ValueError('Use a tag de um modelo local instalado; modelos cloud não são permitidos.')
    return modelo


def validar_config(dados):
    if not isinstance(dados, dict): raise ValueError('Configuração local inválida.')
    conf = {k: dados.get(k, v) for k, v in PADRAO.items()}
    if dados and 'perfil' not in dados: conf['perfil']='legado'
    from ..desempenho import PERFIS
    if not isinstance(conf['perfil'],str) or conf['perfil'] not in PERFIS: raise ValueError('Perfil local inválido.')
    try:
        u = urlsplit(conf['url'])
        if (u.scheme != 'http' or u.hostname != '127.0.0.1' or not u.port
                or u.username is not None or u.password is not None or u.path not in ('', '/')
                or u.query or u.fragment): raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise ValueError('Ollama deve usar HTTP em 127.0.0.1 com porta explícita, sem credenciais.') from None
    conf['url'] = conf['url'].rstrip('/')
    validar_modelo(conf['modelo'])
    if type(conf['contexto']) is not int or conf['contexto'] not in (2048, 4096):
        raise ValueError('Escolha o perfil de 2.048 ou 4.096 tokens.')
    if conf['perfil']=='completo' and conf['contexto']!=4096:raise ValueError('Perfil Completo precisa de contexto 4.096; confirme esse tamanho na configuração.')
    if type(conf['timeout']) is not int or not 30 <= conf['timeout'] <= 600:
        raise ValueError('O tempo limite local deve ficar entre 30 e 600 segundos.')
    return conf


class Ollama:
    def __init__(self, config): self.config = validar_config(config)

    def _abrir(self, endpoint, dados=None, cancelar=None, timeout=10):
        if endpoint not in ('version', 'tags', 'ps', 'show', 'chat', 'embed'):
            raise ValueError('Operação local não permitida.')
        u = urlsplit(self.config['url'])
        connection = http.client.HTTPConnection('127.0.0.1', u.port, timeout=min(timeout, 5))
        timer = None
        expirou = []
        try:
            if cancelar: cancelar.verificar()
            connection.connect()
            sock = connection.sock
            sock.settimeout(timeout)
            def interromper():
                try: sock.shutdown(socket.SHUT_RDWR)
                except OSError: pass
            if cancelar: cancelar.registrar(interromper)
            def prazo():
                expirou.append(True); interromper()
            timer = Timer(timeout, prazo); timer.daemon = True; timer.start()
            body = json.dumps(dados, ensure_ascii=False).encode() if dados is not None else None
            connection.request('POST' if dados is not None else 'GET', '/api/'+endpoint,
                               body, {'Content-Type': 'application/json', 'Connection': 'close'})
            response = connection.getresponse()
            if response.status != 200:
                response.close()
                if 300 <= response.status < 400: raise RuntimeError('Redirecionamento do servidor local bloqueado.')
                if response.status == 404: raise RuntimeError('Modelo ou endpoint não encontrado no Ollama. Confira os modelos instalados.')
                raise RuntimeError(f'Ollama recusou a consulta (HTTP {response.status}). Confira memória e configuração do runtime.')
            return connection, response, timer, expirou
        except (OSError, http.client.HTTPException) as exc:
            if timer: timer.cancel()
            connection.close()
            if cancelar: cancelar.verificar()
            if expirou: raise RespostaIncompleta('Tempo limite do Ollama atingido. Tente uma pergunta menor.','timeout') from exc
            raise RuntimeError('Ollama indisponível. Inicie o servidor local e teste a conexão em Configurações de IA.') from exc
        except Exception:
            if timer: timer.cancel()
            connection.close()
            raise

    def metadados(self, endpoint, dados=None, cancelar=None, timeout=10):
        con, response, timer, _ = self._abrir(endpoint, dados, cancelar, timeout)
        try:
            raw = response.read(1024*1024+1)
            if len(raw) > 1024*1024: raise RuntimeError('Metadados locais acima do limite.')
            value = json.loads(raw)
            if not isinstance(value, dict): raise ValueError()
            return value
        except (ValueError, OSError, http.client.HTTPException) as exc:
            if cancelar: cancelar.verificar()
            raise RuntimeError('O servidor local retornou metadados inválidos ou incompletos.') from exc
        finally:
            if cancelar: cancelar.registrar(None)
            timer.cancel(); response.close(); con.close()

    def diagnostico(self):
        version = self.metadados('version').get('version', '')
        modelos = []
        for m in self.metadados('tags').get('models', [])[:100]:
            try: validar_modelo(m['name'])
            except (ValueError, KeyError): continue
            if m.get('remote_host') or m.get('remote_model'): continue
            modelos.append({k: m.get(k) for k in ('name', 'size', 'digest', 'details')})
        carregados = self.metadados('ps').get('models', [])
        info = {'capacidades': [], 'digest': '', 'modelo_disponivel': False, 'aviso': ''}
        try: info.update(self.modelo(), modelo_disponivel=True)
        except RuntimeError as exc: info['aviso'] = str(exc)
        from ..desempenho import dispositivo, memoria
        return {'versao': version, 'modelos': modelos, **info, 'dispositivo':dispositivo(carregados,self.config['modelo']), 'memoria':memoria(),
                'carregado': any(m.get('name') == self.config['modelo'] for m in carregados),
                'local': True, 'visao_implementada': False}

    def modelo(self,cancelar=None,capacidade='completion'):
        installed = next((m for m in self.metadados('tags',cancelar=cancelar).get('models', []) if m.get('name') == self.config['modelo']), None)
        if not installed: raise ErroLocal('O modelo selecionado não está instalado. Escolha uma tag na lista local.','modelo_indisponivel')
        info = self.metadados('show', {'model': self.config['modelo'], 'verbose': False},cancelar)
        if any(d.get('remote_host') or d.get('remote_model') for d in (installed, info)):
            raise RuntimeError('Este modelo usa processamento cloud e foi bloqueado. Escolha pesos locais.')
        capabilities = info.get('capabilities', [])
        if capacidade not in capabilities: raise RuntimeError('O modelo não informou a capacidade solicitada na API de metadados: '+capacidade)
        return {'capacidades': capabilities, 'digest': installed.get('digest', '')}

    def consultar(self, mensagens, saida, cancelar=None, trecho=None, formato=None):
        from ..desempenho import Amostragem, dispositivo
        cancelar = cancelar or Cancelamento()
        start=time.monotonic(); first=None; pieces=[]; size=0; final={}; con=response=timer=None; expirou=[]
        metrics={'provedor':'ollama','modelo':self.config['modelo'],'digest':None,
                 'num_ctx':self.config['contexto'],'num_predict':saida,'timeout':self.config['timeout'],
                 'perfil':self.config['perfil'],'thinking':None,'motivo':'executando', 'done_reason':None,
                 'tokens_entrada':None,'tokens_saida':None,'tokens_cache':None,
                 'carga_s':None,'entrada_s':None,'geracao_s':None,'total_runtime_s':None,
                 'tokens_s':None,'primeiro_token_s':None,'dispositivo':{'estado':'desconhecido','processador':'desconhecido'}}
        sampler=Amostragem();sampler.__enter__()
        try:
            cancelar.verificar();info=self.modelo(cancelar);metrics['digest']=info['digest'];cancelar.verificar()
            body={'model':self.config['modelo'],'messages':mensagens,'stream':True,'keep_alive':'2m',
                  'options':{'num_ctx':self.config['contexto'],'num_predict':saida,
                             'temperature':.7,'top_p':.8,'top_k':20,'presence_penalty':1.5,'repeat_penalty':1.0}}
            if 'thinking' in info['capacidades']:body['think']=False;metrics['thinking']=False
            if formato is not None:body['format']=formato
            con,response,timer,expirou=self._abrir('chat',body,cancelar,self.config['timeout'])
            while True:
                cancelar.verificar();line=response.readline(65537)
                if not line:break
                if len(line)>65536:raise RespostaIncompleta('Trecho local acima do limite.','limite_trecho')
                data=json.loads(line)
                if data.get('error'):
                    motivo='memoria' if 'out of memory' in str(data['error']).lower() else 'runtime'
                    raise RespostaIncompleta('Runtime interrompeu a geração'+(' por falta de memória confirmada.' if motivo=='memoria' else '.'),motivo)
                part=data.get('message',{}).get('content','')
                if not isinstance(part,str):raise ValueError()
                if part:
                    size+=len(part)
                    if size>120000:raise RespostaIncompleta('Resposta acima do limite.','limite_texto')
                    if first is None:
                        first=time.monotonic()-start
                        try:metrics['dispositivo']=dispositivo(self.metadados('ps',timeout=1).get('models',[]),self.config['modelo'])
                        except RuntimeError:pass
                    pieces.append(part)
                    if trecho:trecho(part)
                if data.get('done') is True:final=data;break
            cancelar.verificar()
            if expirou:raise RespostaIncompleta('Tempo limite local atingido; texto parcial preservado.','timeout')
            if not final or not pieces:raise RespostaIncompleta('Conexão encerrada sem uma resposta completa.','fim_abrupto')
            reason=final.get('done_reason')
            if reason is not None and (not isinstance(reason,str) or len(reason)>80):raise RespostaIncompleta('Motivo de encerramento inválido.','resposta_invalida')
            metrics['done_reason']=reason
            if reason not in ('stop',None):
                raise RespostaIncompleta('Limite de saída atingido; texto parcial preservado.' if reason=='length' else 'Encerramento inesperado do runtime.', 'limite_saida' if reason=='length' else 'fim_inesperado')
            metrics['motivo']='concluida'
            return {'texto':''.join(pieces),'metricas':metrics}
        except Exception as exc:
            from .contratos import ConsultaCancelada
            if cancelar.evento.is_set():exc=ConsultaCancelada('Consulta cancelada; texto parcial preservado.')
            elif isinstance(exc,(OSError,http.client.HTTPException)):
                exc=RespostaIncompleta('Tempo limite local atingido.' if expirou else 'Conexão local interrompida.', 'timeout' if expirou else 'conexao')
            elif isinstance(exc,(ValueError,TypeError,AttributeError)) and not isinstance(exc,RespostaIncompleta):
                exc=RespostaIncompleta('O runtime retornou dados inválidos.','resposta_invalida')
            metrics['motivo']='cancelada' if isinstance(exc,ConsultaCancelada) else getattr(exc,'motivo','runtime_indisponivel')
            exc.metricas=metrics
            raise exc
        finally:
            final={k:v for k,v in final.items() if k=='done_reason' and isinstance(v,str) and len(v)<=80 or type(v) is int and v>=0}
            duration=final.get('eval_duration',0)/1e9
            metrics['frame_final']=bool(final)
            metrics.update(segundos=time.monotonic()-start,primeiro_token_s=first,done_reason=final.get('done_reason'),
                tokens_entrada=final.get('prompt_eval_count'),tokens_saida=final.get('eval_count'),tokens_cache=final.get('prompt_eval_cached_count'),
                tokens_s=final.get('eval_count',0)/duration if duration else None)
            for target,key in [('carga_s','load_duration'),('entrada_s','prompt_eval_duration'),('geracao_s','eval_duration'),('total_runtime_s','total_duration')]:
                metrics[target]=final[key]/1e9 if type(final.get(key)) is int else None
            sampler.__exit__();metrics['memoria']=dict(sampler.dados)
            cancelar.registrar(None)
            if timer:timer.cancel()
            if response:response.close()
            if con:con.close()
