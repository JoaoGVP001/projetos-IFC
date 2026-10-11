"""Fluxo de produção com HTTP local simulado, sem chaves ou dados pessoais."""
import json
import sqlite3
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from tutor_calculo.armazenamento import Historico
from tutor_calculo.servico import Aplicacao
from tutor_calculo.ia import preparar_consulta, perguntar, limitar_contexto
from tutor_calculo.preferencias_ia import PreferenciasIA
from tutor_calculo.provedores.ollama import Ollama, validar_config
from tutor_calculo.provedores.contratos import Cancelamento, ConsultaCancelada, RespostaIncompleta


class RuntimeSimulado:
    def __init__(self,porta=0):
        self.requests=[];self.release=threading.Event();self.hold=False
        self.text='Resposta **local**: $2+2=4$.';self.reason='stop';self.remote=False;self.invalid=False
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def reply(self,data,status=200):
                self.send_response(status);self.end_headers();self.wfile.write(json.dumps(data).encode());self.wfile.flush()
            def do_GET(self):
                if self.path=='/api/version':self.reply({'version':'simulado'})
                elif self.path in ('/api/tags','/api/ps'):self.reply({'models':[{'name':'teste:4b','size':100,'digest':'digest-teste','details':{'quantization_level':'Q4'}}]})
                else:self.reply({},404)
            def do_POST(self):
                data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                owner.requests.append((self.path,data))
                if self.path=='/api/show':self.reply({'capabilities':['completion','thinking'],**({'remote_host':'https://example.com'} if owner.remote else {})});return
                if self.path!='/api/chat':self.reply({},404);return
                try:
                    self.send_response(200);self.end_headers()
                    if owner.invalid:self.wfile.write(b'invalid-json\n');self.wfile.flush();return
                    line=json.dumps({'message':{'content':owner.text},'done':False}).encode()+b'\n'
                    self.wfile.write(line[:8]);self.wfile.flush();self.wfile.write(line[8:]);self.wfile.flush()
                    if owner.hold:owner.release.wait(8)
                    self.wfile.write(json.dumps({'message':{'content':''},'done':True,'done_reason':owner.reason,
                        'eval_count':10,'eval_duration':1000000000,'prompt_eval_count':200}).encode()+b'\n');self.wfile.flush()
                except (BrokenPipeError,ConnectionResetError):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',porta),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.config={'modelo':'teste:4b','url':f'http://127.0.0.1:{self.server.server_port}','contexto':4096,'timeout':30}
    def close(self):self.release.set();self.server.shutdown();self.server.server_close()


class OllamaTest(unittest.TestCase):
    def setUp(self):self.runtime=RuntimeSimulado();self.addCleanup(self.runtime.close)
    def test_sem_chave_sem_nuvem_e_metricas_stream(self):
        pieces=[];metrics={}
        with patch('tutor_calculo.ia.configuracao') as keys,patch('openai.OpenAI') as cloud,patch('tutor_calculo.gemini.consultar') as gemini:
            answer=perguntar('Quanto é 2+2?',provedor='ollama',modelo='teste:4b',local=self.runtime.config,trecho=pieces.append,metricas=metrics.update)
            keys.assert_not_called();cloud.assert_not_called();gemini.assert_not_called()
        self.assertEqual(answer,self.runtime.text);self.assertEqual(''.join(pieces),answer);self.assertEqual(metrics['tokens_s'],10)
        data=self.runtime.requests[-1][1];self.assertTrue(data['stream']);self.assertFalse(data['think']);self.assertEqual(data['options']['num_ctx'],4096)
    def test_enderecos_tags_cloud_e_credenciais_bloqueados(self):
        for url in ['https://127.0.0.1:11434','http://example.com:11434','http://localhost:11434','http://@127.0.0.1:11434','http://u:p@127.0.0.1:11434','http://127.0.0.1:11434/else','http://127.0.0.1:11434?q=1']:
            with self.subTest(url=url),self.assertRaises(ValueError):validar_config({'url':url})
        for model in ['teste:cloud','teste:CLOUD','teste:4b-cloud','../teste','teste;exe']:
            with self.subTest(model=model),self.assertRaises(ValueError):validar_config({'modelo':model})
        self.assertEqual(validar_config({'modelo':'qwen/teste:4b-q4_K_M'})['modelo'],'qwen/teste:4b-q4_K_M')
    def test_remoto_camuflado_nao_gera(self):
        self.runtime.remote=True
        with self.assertRaisesRegex(RuntimeError,'cloud'):Ollama(self.runtime.config).consultar([{'role':'user','content':'x'}],100)
        self.assertFalse(any(p=='/api/chat' for p,_ in self.runtime.requests))
    def test_diagnostico_lista_mesmo_com_modelo_ausente(self):
        d=Ollama({**self.runtime.config,'modelo':'ausente:4b'}).diagnostico()
        self.assertEqual(d['modelos'][0]['name'],'teste:4b');self.assertFalse(d['modelo_disponivel']);self.assertIn('instalado',d['aviso'])
    def test_limite_e_json_invalido_nao_concluem(self):
        self.runtime.reason='length'
        with self.assertRaises(RespostaIncompleta):Ollama(self.runtime.config).consultar([],100)
        self.runtime.invalid=True
        with self.assertRaises(RespostaIncompleta):Ollama(self.runtime.config).consultar([],100)
    def test_cancelamento_interrompe_socket_bloqueado(self):
        self.runtime.hold=True;token=Cancelamento();received=threading.Event();errors=[]
        def run():
            try:Ollama(self.runtime.config).consultar([],100,token,lambda _:received.set())
            except Exception as exc:errors.append(exc)
        thread=threading.Thread(target=run);thread.start();self.assertTrue(received.wait(3));token.cancelar();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertIsInstance(errors[0],ConsultaCancelada)
    def test_orcamento_previa_preserva_pergunta_e_omite_dados(self):
        messages=[]
        for _ in range(8):messages.extend([{'papel':'user','texto':'antigo '*300},{'papel':'assistant','texto':'resposta '*300}])
        sources=[{'referencia':'M1','material_id':'x','nome':'Fonte','pagina':1,'texto':'conteúdo '*2000,'url':'','tipo':'txt'}]
        p=preparar_consulta('Explique o conteúdo',historico=messages,fontes=sources,provedor='ollama',local=self.runtime.config)
        o=p['orcamento'];self.assertLessEqual(o['entrada_estimada']+o['reserva_saida']+o['margem'],o['contexto'])
        self.assertGreater(o['pares_omitidos'],0);self.assertGreater(o['trechos_abreviados'],0);self.assertIn('Explique o conteúdo',p['pergunta'])
        with self.assertRaisesRegex(ValueError,'nada foi enviado'):preparar_consulta('á'*15000,provedor='ollama',local=self.runtime.config)
    def test_fontes_autorizadas_e_citacao_inexistente(self):
        self.runtime.text='Segundo [M1], quatro. Também [M99].'
        sources=[{'referencia':'M1','material_id':'x','nome':'Fonte','pagina':1,'texto':'2+2=4','url':'','tipo':'txt'}]
        answer=perguntar('Explique',fontes=sources,provedor='ollama',modelo='teste:4b',local=self.runtime.config)
        self.assertIn('referencia indisponivel',answer);self.assertIn('Fonte',answer)
        self.assertIn('DADOS NAO CONFIAVEIS',self.runtime.requests[-1][1]['messages'][0]['content'])


class FluxoLocalTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'h.sqlite3'
        self.runtime=RuntimeSimulado();self.app=Aplicacao(self.path)
        self.app._ia_preferencias.salvar('ollama',self.runtime.config)
        self.cid=self.op('chat_criar')['conversa']['id']
    def tearDown(self):
        self.app.fechar();self.runtime.release.set();self.app._executor.shutdown(wait=True);self.runtime.close();self.tmp.cleanup()
    def op(self,op,**d):return self.app.executar(op,d)
    def wait(self,predicate):
        for _ in range(200):
            state=self.op('estado')
            if predicate(state):return state
            time.sleep(.01)
        self.fail('Timeout de estado')
    def send(self,**d):return self.op('enviar',id=self.cid,texto='Quanto é 2+2?',modo='Explicar',**d)['tarefa']
    def test_idempotencia_e_reinicio_preservam_chat_e_preferencia(self):
        rid='id-estavel';self.send(requisicao=rid);self.wait(lambda s:not s['ocupado']);self.send(requisicao=rid)
        state=self.op('estado');self.assertEqual(len(state['mensagens']),2);self.assertEqual(state['mensagens'][-1]['provedor'],'ollama')
        self.op('configurar',provedor='ollama',modelo='teste:4b',url=self.runtime.config['url'],escopo='chat',contexto=2048,timeout=60)
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        self.assertEqual(self.op('estado')['config']['local']['contexto'],2048);self.assertEqual(self.op('estado')['conversa']['id'],self.cid)
    def test_previa_resolver_com_ia_corresponde_ao_envio(self):
        from tutor_calculo.app import EXEMPLO
        p=self.op('previa',id=self.cid,texto=EXEMPLO,modo='Resolver com IA')
        self.assertIn('Somente Ollama',p['destino']);self.assertIsNotNone(p['orcamento'])
        task=self.op('enviar',id=self.cid,texto=EXEMPLO,modo='Resolver com IA')['tarefa']
        self.wait(lambda s:not s['ocupado'])
        with self.app._banco() as (h,c,b):
            row=h.db.execute('SELECT snapshot FROM consultas_ia WHERE id=?',(task,)).fetchone()
            snap=json.loads(row[0]);self.assertFalse(snap['calculo_local'])
            self.assertEqual(snap['preparada']['instrucoes'],p['instrucoes'])
        symbolic=self.op('previa',id=self.cid,texto=EXEMPLO,modo='Resolver')
        self.assertIn('sem consulta à IA',symbolic['destino'])

    def test_cancelar_repetir_sem_duplicar_usuario_ou_aproveitar_parcial(self):
        self.runtime.hold=True;tid=self.send()
        self.wait(lambda s:bool(s['tarefas'][-1].get('parcial')));self.op('ia_cancelar',id=tid)
        state=self.wait(lambda s:not s['ocupado']);self.assertEqual(state['mensagens'][-1]['estado'],'cancelada')
        self.assertEqual(state['conversa']['rascunho'],'Quanto é 2+2?');self.assertEqual(limitar_contexto(state['mensagens']),[])
        self.runtime.hold=False;self.runtime.release.set();self.op('ia_repetir',id=tid,requisicao='nova')
        state=self.wait(lambda s:not s['ocupado']);self.assertEqual(sum(m['papel']=='user' for m in state['mensagens']),1)
        self.assertEqual(state['mensagens'][-1]['estado'],'ok');self.assertEqual(state['conversa']['rascunho'],'')
        context=limitar_contexto(state['mensagens']);self.assertEqual(context[0]['content'],'Quanto é 2+2?')
        self.assertEqual(len(context),2)
    def test_falha_local_nao_chama_online_e_preserva_pergunta(self):
        self.app._ia_preferencias.salvar('ollama',{**self.runtime.config,'modelo':'ausente:4b'})
        with patch('openai.OpenAI') as cloud,patch('tutor_calculo.gemini.consultar') as gemini:
            self.send();state=self.wait(lambda s:not s['ocupado']);cloud.assert_not_called();gemini.assert_not_called()
        self.assertEqual(state['mensagens'][-1]['estado'],'erro');self.assertEqual(state['conversa']['rascunho'],'Quanto é 2+2?')
    def test_resolver_fallback_usa_provedor_capturado_e_exemplo_nao_usa_api(self):
        from tutor_calculo.app import EXEMPLO
        with patch('openai.OpenAI') as cloud,patch('tutor_calculo.gemini.consultar') as gemini:
            self.op('enviar',id=self.cid,texto='Quanto é 2+2?',modo='Resolver');state=self.wait(lambda s:not s['ocupado'])
            self.assertEqual(state['mensagens'][-1]['provedor'],'ollama');cloud.assert_not_called();gemini.assert_not_called()
            count=len(self.runtime.requests)
            self.op('enviar',id=self.cid,texto=EXEMPLO,modo='Resolver');state=self.wait(lambda s:not s['ocupado'])
            self.assertEqual(state['mensagens'][-1]['modelo'],'SymPy');self.assertEqual(len(self.runtime.requests),count)
    def test_recuperar_execucao_interrompida_uma_unica_vez(self):
        self.send(requisicao='simular-crash');self.wait(lambda s:not s['ocupado'])
        with self.app._banco() as (h,c,b):
            with h.db:
                h.db.execute("DELETE FROM mensagens WHERE papel='assistant'")
                h.db.execute("UPDATE consultas_ia SET estado='executando',parcial='Texto recuperado'")
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        state=self.op('estado');self.assertEqual(state['mensagens'][-1]['estado'],'incompleta');self.assertIn('Texto recuperado',state['mensagens'][-1]['texto'])
        self.app.fechar();self.app=Aplicacao(self.path);self.assertEqual(len(self.op('estado')['mensagens']),2)
    def test_atividade_json_dica_feedback_sem_chave_e_sem_salvar_sozinha(self):
        self.runtime.text=json.dumps({'titulo':'Piloto','descricao':'','objetivo':'Somas','assuntos':'Soma','etiquetas':'','dificuldade':'basica',
            'exercicios':[{'id':'q1','enunciado':'Quanto é 2+2?','formato':'escolha','assunto':'Soma','dificuldade':'basica',
            'alternativas':[{'id':'a','texto':'4'},{'id':'b','texto':'5'}],'explicacao':'Dois mais dois é quatro.','resposta':'a','referencias':[]}]})
        j=self.op('estudo_previa',tipo='geracao',assunto='Soma',quantidade=1,formatos=['escolha'])
        self.assertTrue(j['previa']['local']);self.op('estudo_consultar',id=j['id']);self.wait(lambda s:not s['ocupado'])
        done=self.op('estudo_job',id=j['id']);self.assertEqual(done['estado'],'concluida',done['erro']);self.assertEqual(self.op('atividades')['total'],0)
        self.assertIn('format',self.runtime.requests[-1][1])
        a=self.op('atividade_salvar',conteudo=done['resultado'],proposta=j['id']);t=self.op('tentativa_iniciar',atividade=a['id'])
        self.op('tentativa_salvar',id=t['id'],exercicio='q1',resposta='a',posicao=0);self.runtime.text='Confira a soma.'
        for kind in ('dica','feedback'):
            j=self.op('estudo_previa',tipo=kind,tentativa=t['id'],exercicio='q1');self.op('estudo_consultar',id=j['id']);self.wait(lambda s:not s['ocupado'])
            self.assertEqual(self.op('estudo_job',id=j['id'])['estado'],'concluida')
        result=self.op('tentativa_obter',id=t['id']);self.assertEqual(result['respostas']['q1']['dicas'][0]['provedor'],'ollama')
        self.assertEqual(len(result['respostas']['q1']['feedbacks']),1)
    def test_config_local_nao_altera_env_ou_envia_chave(self):
        with patch('tutor_calculo.servico.salvar_configuracao') as secret:
            conf=self.op('configurar',provedor='ollama',modelo='teste:4b',url=self.runtime.config['url'],escopo='chat')
            secret.assert_not_called()
        self.assertEqual(conf['escopo'],'chat');self.assertEqual(conf['provedor'],'ollama')
        self.assertNotIn('API_KEY',(self.path.parent/'ia.json').read_text())
    def test_atividade_limite_e_json_invalido_nao_salvam(self):
        with self.assertRaisesRegex(ValueError,'1 a 3'):self.op('estudo_previa',tipo='geracao',assunto='Soma',quantidade=4)
        self.runtime.text='JSON inválido';j=self.op('estudo_previa',tipo='geracao',assunto='Soma',quantidade=1)
        self.op('estudo_consultar',id=j['id']);self.wait(lambda s:not s['ocupado'])
        self.assertEqual(self.op('estudo_job',id=j['id'])['estado'],'erro');self.assertEqual(self.op('atividades')['total'],0)


class MigracaoLocalTest(unittest.TestCase):
    def test_v6_backup_e_rollback_preservam_dados(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'h.sqlite3';h=Historico(path);cid=h.criar();h.adicionar(cid,'user','Intacto');h.rascunho(cid,'Rascunho');h.fechar()
            with sqlite3.connect(path) as db:

                for table in ('semantica_config','semantica_vetores','semantica_preparo','semantica_trabalho'):db.execute('DROP TABLE '+table)
                db.execute('DROP TRIGGER semantica_texto_alterado')
                db.execute('DROP TABLE consultas_ia');db.execute('DROP TABLE chat_ia');db.execute('DROP TABLE IF EXISTS calculos');db.execute('PRAGMA user_version=6')
            def fail(db):db.execute('CREATE TABLE temporaria(id)');raise RuntimeError('Falha simulada')
            with patch('tutor_calculo.preferencias_ia.migrar_ia',side_effect=fail),self.assertRaises(RuntimeError):Historico(path)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],6)
                self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='temporaria'").fetchone())
            h=Historico(path)
            try:self.assertEqual(h.obter(cid)['rascunho'],'Rascunho');self.assertEqual(h.mensagens(cid)[0]['texto'],'Intacto')
            finally:h.fechar()
            with sqlite3.connect(str(path)+'.v6.backup') as db:self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],6)
    def test_preferencias_corrompidas_nao_voltam_para_cloud(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=PreferenciasIA(tmp);p.salvar('ollama');p.caminho.write_text('invalid-json')
            with self.assertRaises(RuntimeError):p.ler()


if __name__=='__main__':unittest.main()
