import json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from test_ollama import RuntimeSimulado
from tutor_calculo.provedores.ollama import Ollama,validar_config
from tutor_calculo.provedores.contratos import RespostaIncompleta,Cancelamento
from tutor_calculo.desempenho import politica,dispositivo
from tutor_calculo.ia import preparar_consulta,perguntar
from tutor_calculo.servico import Aplicacao

class Estabilidade(unittest.TestCase):
 def test_perfil_antigo_e_por_tarefa(self):
  old=validar_config({'contexto':2048});self.assertEqual(old['perfil'],'legado');self.assertEqual(politica(old)['reserva_saida'],640)
  quick=validar_config({'contexto':4096,'perfil':'rapido'});self.assertEqual(politica(quick)['reserva_saida'],640)
  self.assertEqual(politica(quick,'Organizar página')['reserva_saida'],1024)
  self.assertEqual(politica(quick,'Dica de atividade')['reserva_saida'],384)
  with self.assertRaises(ValueError):validar_config({'perfil':'inventado'})
 def test_prompt_completo_no_orcamento_e_sem_promessa(self):
  p=preparar_consulta('Explique indução',provedor='ollama',local={'perfil':'rapido','contexto':4096})
  self.assertIn('hipótese',p['instrucoes']);self.assertIn('Não escreva Mermaid',p['instrucoes'])
  o=p['orcamento'];self.assertLessEqual(o['entrada_estimada']+o['reserva_saida']+o['margem'],4096)
 def test_dispositivo_nao_inventa(self):
  self.assertEqual(dispositivo([], 'm')['estado'],'nao_carregado')
  for size,vram,expected in [(100,0,'CPU'),(100,100,'GPU'),(100,30,'CPU/GPU'),(None,None,'desconhecido')]:
   self.assertEqual(dispositivo([{'name':'m','size':size,'size_vram':vram}],'m')['processador'],expected)
 def test_metricas_length_e_json_invalido(self):
  r=RuntimeSimulado();self.addCleanup(r.close);r.reason='length';m={}
  with self.assertRaises(RespostaIncompleta) as e:perguntar('x',provedor='ollama',local=r.config,metricas=m.update)
  self.assertEqual(e.exception.motivo,'limite_saida');self.assertEqual(m['tokens_saida'],10);self.assertEqual(m['done_reason'],'length');self.assertIn('memoria',m)
  r.invalid=True
  with self.assertRaises(RespostaIncompleta) as e:Ollama(r.config).consultar([],100)
  self.assertEqual(e.exception.metricas['motivo'],'resposta_invalida');self.assertIsNone(e.exception.metricas['tokens_saida'])
 def test_timeout_com_metricas_e_frame_ausente(self):
  import threading
  r=RuntimeSimulado();self.addCleanup(r.close);r.hold=True
  def timer(t,f):return threading.Timer(.15,f)
  with patch('tutor_calculo.provedores.ollama.Timer',side_effect=timer):
   with self.assertRaises(RespostaIncompleta) as e:Ollama(r.config).consultar([],100)
  self.assertEqual(e.exception.metricas['motivo'],'timeout');self.assertFalse(e.exception.metricas['frame_final']);self.assertIsNotNone(e.exception.metricas['primeiro_token_s'])
 def test_modelo_ausente_tem_motivo_distinto(self):
  r=RuntimeSimulado();self.addCleanup(r.close)
  with self.assertRaises(RuntimeError) as e:Ollama({**r.config,'modelo':'ausente:4b'}).consultar([],100)
  self.assertEqual(e.exception.metricas['motivo'],'modelo_indisponivel')
 def test_configuracao_json_minimo_e_contexto_insuficiente(self):
  p=preparar_consulta('Organize uma página simples',modo='Organizar página',provedor='ollama',local={'perfil':'rapido','contexto':4096})
  self.assertEqual(p['orcamento']['reserva_saida'],1024)
  with self.assertRaisesRegex(ValueError,'excedem'):preparar_consulta('enunciado '*1500,provedor='ollama',local={'perfil':'rapido','contexto':2048})
 def test_memoria_indisponivel_nao_e_zero(self):
  from tutor_calculo.desempenho import memoria
  with patch('pathlib.Path.read_text',side_effect=OSError):
   m=memoria();self.assertIsNone(m['ram_total']);self.assertIsNone(m['swap_usada'])
 def test_retirar_fonte_impede_envio_da_previa(self):
  with tempfile.TemporaryDirectory() as d:
   app=Aplicacao(Path(d)/'db.sqlite3');self.addCleanup(app.fechar);cid=app.executar('chat_criar',{})['conversa']['id'];app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','escopo':'padrao'})
   file=Path(d)/'fonte.txt';file.write_text('Indução matemática exige uma hipótese para k arbitrário.')
   with app._banco() as (h,c,b):
    mid,_=b.adicionar_arquivo(file,cid);b.processar(mid);b.vincular(mid,cid,True)
    f=b.recuperar(cid,'indução matemática');sel=app._selecao(h,cid);snap={'pergunta':'Explique indução','modo':'Resolver com IA','historico':[],'fontes':f,'caderno':None,'selecao':sel}
    uid=h.adicionar(cid,'user','Explique indução');rid=h.adicionar(cid,'assistant','Primeira parte','incompleta','ollama','teste:4b')
    with h.db:h.db.execute("INSERT INTO consultas_ia(id,conversa_id,usuario_id,resposta_id,snapshot,estado,parcial,erro) VALUES('fonte',?,?,?,?,'incompleta','Primeira parte','corte')",(cid,uid,rid,json.dumps(snap)))
   prev=app.executar('ia_ajuste_previa',{'id':'fonte','acao':'curta'})
   with app._banco() as (h,c,b):b.vincular(mid,cid,False)
   with self.assertRaisesRegex(ValueError,'desmarcados'):app.executar('ia_ajuste_enviar',{'id':prev['id']})
 def test_aviso_legado_separado_e_continuacao_idempotente(self):
  with tempfile.TemporaryDirectory() as d:
   app=Aplicacao(Path(d)/'db.sqlite3');self.addCleanup(app.fechar)
   app.executar('chat_criar',{});cid=app.executar('estado',{})['conversa']['id']
   app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','perfil':'legado','escopo':'padrao'})
   with app._banco() as (h,c,b):
    selection=app._selecao(h,cid);snap={'pergunta':'Explique indução','modo':'Resolver com IA','historico':[],'fontes':None,'caderno':None,'selecao':selection,'preparada':preparar_consulta('Explique indução',provedor='ollama',local=selection['local'])}
    uid=h.adicionar(cid,'user','Explique indução');mid=h.adicionar(cid,'assistant','```mermaid\nA-->B\n\nLimite atingido','incompleta','ollama','teste:4b')
    with h.db:h.db.execute("INSERT INTO consultas_ia(id,conversa_id,usuario_id,resposta_id,snapshot,estado,parcial,erro) VALUES('old',?,?,?,?,'incompleta',?,'Limite atingido')",(cid,uid,mid,json.dumps(snap),'```mermaid\nA-->B'))
   msg=app.executar('estado',{})['mensagens'][-1];self.assertEqual(msg['texto'],'```mermaid\nA-->B');self.assertEqual(msg['interrupcao']['mensagem'],'Limite atingido')
   prev=app.executar('ia_ajuste_previa',{'id':'old','acao':'continuar'});self.assertIn('A-->B',prev['pergunta']);self.assertEqual(prev['historico'],[])
   with patch('tutor_calculo.servico.perguntar',return_value='Conclusão em uma nova parte.'):
    app.executar('ia_ajuste_enviar',{'id':prev['id']});app.executar('ia_ajuste_enviar',{'id':prev['id']})
    for _ in range(100):
     if not app.executar('estado',{})['ocupado']:break
     time.sleep(.02)
   state=app.executar('estado',{});self.assertEqual(len(state['mensagens']),4);self.assertEqual(state['mensagens'][-1]['origem_consulta'],'old');self.assertEqual(state['mensagens'][-1]['origem_mensagem'],mid)
   short=app.executar('ia_ajuste_previa',{'id':'old','acao':'curta'})
   with patch('tutor_calculo.servico.perguntar',return_value='Uma resposta completa, sem streaming.'):
    app.executar('ia_ajuste_enviar',{'id':short['id']})
    for _ in range(100):
     if not app.executar('estado',{})['ocupado']:break
     time.sleep(.02)
   follow=app.executar('ia_ajuste_previa',{'id':short['id'],'acao':'continuar'})
   self.assertIn('sem streaming',follow['pergunta']);self.assertEqual(app.executar('estado',{})['config']['local']['perfil'],'legado')
   p=app.executar('ia_ajuste_previa',{'id':'old','acao':'curta'});app.executar('configurar',{'provedor':'ollama','modelo':'outro:4b','escopo':'padrao'})
   with self.assertRaisesRegex(ValueError,'Configuração mudou'):app.executar('ia_ajuste_enviar',{'id':p['id']})
 def test_ilustracao_persistencia_pagina_sem_verificacao(self):
  with tempfile.TemporaryDirectory() as d:
   app=Aplicacao(Path(d)/'db.sqlite3');self.addCleanup(app.fechar);cid=app.executar('chat_criar',{})['conversa']['id']
   j=app.executar('inducao_executar',{'conversa':cid,'spec':{'inicio':1,'proposicao':'P(n): soma dos naturais'}})
   for _ in range(400):
    r=app.executar('inducao_obter',{'id':j['id']})
    if r['estado']!='executando':break
    time.sleep(.02)
   self.assertEqual(r['estado'],'concluida');self.assertTrue(r['imagem'].startswith('data:image/png;'));self.assertEqual(r['resultado']['verificacao'],'nao_verificada')
   p=app.executar('pagina_criar',{'caderno':None});p=app.executar('pagina_calculo',{'id':p['id'],'calculo':j['id']})
   self.assertIn('Não verifica',next(iter(p['render']['recursos'].values()))['resumo'])
   with self.assertRaises(ValueError):app.executar('inducao_executar',{'conversa':cid,'spec':{'inicio':True}})
