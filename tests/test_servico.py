"""Contratos da ponte, persistencia e concorrencia sem janela ou API real."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from tempfile import TemporaryDirectory
import json
import time
import unittest
from unittest.mock import patch

from tutor_calculo.armazenamento import Historico
from tutor_calculo.materiais import Biblioteca
from tutor_calculo.ponte import Ponte
from tutor_calculo.servico import Aplicacao


class ServicoTest(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.pasta=Path(self.tmp.name)
        self.config=patch('tutor_calculo.servico.configuracao',return_value=('segredo-simulado','modelo-teste'))
        self.provider=patch('tutor_calculo.servico.provedor_ativo',return_value='gemini')
        self.config.start();self.provider.start()
        self.app=Aplicacao(self.pasta/'historico.sqlite3')
        self.p=Ponte(self.app)

    def tearDown(self):
        self.app.fechar()
        self.app._executor.shutdown(wait=True)
        self.config.stop();self.provider.stop();self.tmp.cleanup()

    def op(self,op,**dados):return self.app.executar(op,dados)
    def chat(self,caderno=None):return self.op('chat_criar',caderno=caderno)['conversa']['id']
    def esperar(self,predicado):
        limite=time.monotonic()+10
        while time.monotonic()<limite:
            estado=self.op('estado')
            if predicado(estado):return estado
            time.sleep(.03)
        self.fail('Tarefa nao terminou dentro do limite.')

    def test_contrato_nao_expoe_chave_nem_operacoes_arbitrarias(self):
        s=self.p.request('estado',{})
        self.assertTrue(s['ok']);self.assertNotIn('segredo-simulado',json.dumps(s))
        for op,d in [('exec',{}),('importar',{'caminhos':['/etc/passwd']}),('estado',[]),('estado',{'busca':None}),('abrir_link',{'url':'javascript:alert(1)'}),('abrir_original',{'id':'/etc/passwd'})]:
            with self.subTest(op=op):self.assertFalse(self.p.request(op,d)['ok'])
        self.assertEqual([n for n in dir(self.p) if not n.startswith('_')],['request'])

    def test_dados_invalidos_nao_alteram_banco(self):
        cid=self.chat()
        for op,d in [('chat_acao',{'id':cid,'acao':'fixar','valor':'sim'}),('enviar',{'id':cid,'texto':'','modo':'Explicar'}),('materiais',{'pagina':-1}),('preferencias',{'tema':'invalido'}),('chat_acao',{'id':cid,'acao':'excluir'})]:
            with self.subTest(op=op),self.assertRaises(ValueError):self.app.executar(op,d)
        self.assertIsNotNone(self.op('estado')['conversa'])

    def test_caderno_vazio_nao_cria_chat_e_previa_mostra_contexto(self):
        s=self.op('caderno_salvar',nome='Estudo novo',objetivo='Inducao',preferencia='dicas')
        self.assertIsNone(s['conversa']);bid=s['navegacao']['caderno_id']
        self.op('navegar',caderno=bid)
        self.assertEqual(self.op('estado')['conversas'],[])
        self.assertIn('Inducao',self.op('previa',id=None,texto='Dicas')['pedagogia'])
        with HistoricoFechado(self.app.caminho) as h:self.assertEqual(h.db.execute('SELECT count(*) FROM conversas').fetchone()[0],0)

    def test_rascunhos_fixacao_arquivo_tema_e_ids_apos_reinicio(self):
        cid=self.chat();outro=self.chat()
        self.op('rascunho',id=cid,texto='Meu rascunho')
        self.op('rascunho',id=outro,texto='Outro assunto')
        self.op('chat_acao',id=cid,acao='renomear',titulo='Titulo longo preservado')
        self.op('chat_acao',id=cid,acao='fixar',valor=True)
        self.op('chat_acao',id=outro,acao='arquivar',valor=True)
        self.op('navegar',caderno=None,conversa=cid)
        self.op('preferencias',tema='escuro',recolhida=True)
        self.app.fechar();self.app=Aplicacao(self.app.caminho);self.p=Ponte(self.app)
        s=self.op('estado');self.assertEqual(s['conversa']['id'],cid)
        self.assertEqual(s['conversa']['rascunho'],'Meu rascunho');self.assertTrue(s['conversa']['fixada'])
        self.assertEqual(s['preferencias'],{'tema':'escuro','recolhida':True})
        self.assertEqual(self.op('navegar',caderno=None,arquivadas=True)['conversas'][0]['id'],outro)

    def test_threads_da_ponte_usam_conexoes_proprias(self):
        cid=self.chat()
        def salvar(n):
            self.op('rascunho',id=cid,texto=str(n))
            return self.op('estado')['conversa']['id']
        with ThreadPoolExecutor(max_workers=8) as ex:self.assertEqual(set(ex.map(salvar,range(40))),{cid})
        with HistoricoFechado(self.app.caminho) as h:self.assertEqual(h.db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_documento_fluxo_real_busca_dedup_movimento_reinicio_exclusao(self):
        cid=self.chat();arq=self.pasta/'notas.txt';arq.write_text('Derivada: taxa de variacao de uma funcao.')
        self.app.importar([str(arq)])
        s=self.esperar(lambda s:s['anexos'] and s['anexos'][0]['estado']=='pronto')
        m=s['anexos'][0];mid=m['id'];self.assertFalse(m['selecionado'])
        self.assertNotIn('caminho',m);self.assertNotIn('sha256',m)
        self.assertEqual(self.op('materiais',busca='variacao')['total'],1)
        self.assertIn('Derivada',self.op('material_detalhe',id=mid,pagina=1)['texto'])
        self.app.importar([str(arq)]);self.assertEqual(self.op('materiais')['total'],1)
        self.op('material_acao',id=mid,acao='selecionar',valor=True)
        self.assertIn('variacao',str(self.op('previa',id=cid,texto='Explique derivada taxa variacao')['fontes']))
        bid=self.op('caderno_salvar',nome='Destino')['navegacao']['caderno_id']
        self.op('chat_acao',id=cid,acao='mover',destino=bid)
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.app.caminho)
        self.assertTrue(self.op('estado')['anexos'][0]['selecionado'])
        self.assertIn(bid,self.op('estado')['anexos'][0]['cadernos'])
        self.op('material_acao',id=mid,acao='excluir',confirmado=True)
        self.assertEqual(self.op('materiais',busca='variacao')['total'],0)
        self.assertTrue(arq.is_file())

    def test_mover_e_excluir_caderno_preserva_historico_e_selecao(self):
        bid=self.op('caderno_salvar',nome='Novo')['navegacao']['caderno_id'];cid=self.chat(bid)
        self.op('rascunho',id=cid,texto='intacto')
        with HistoricoFechado(self.app.caminho) as h:h.adicionar(cid,'user','Antiga')
        self.op('caderno_acao',id=bid,acao='excluir',confirmado=True)
        s=self.op('estado');self.assertIsNone(s['conversa']['caderno_id'])
        self.assertEqual(s['conversa']['rascunho'],'intacto');self.assertEqual(s['mensagens'][0]['texto'],'Antiga')

    def test_consulta_snapshot_isolado_e_bloqueio_ate_terminar(self):
        bid=self.op('caderno_salvar',nome='Inducao')['navegacao']['caderno_id'];cid=self.chat(bid)
        outro=self.chat(bid);self.op('navegar',conversa=cid)
        iniciou=Event();liberar=Event()
        def simulado(q,**kwargs):iniciou.set();liberar.wait(5);return 'Resposta simulada'
        with patch('tutor_calculo.servico.perguntar',side_effect=simulado) as api:
            self.op('enviar',id=cid,texto='Como demonstrar por inducao?',modo='Explicar')
            try:
                self.assertTrue(iniciou.wait(3))
                with self.assertRaises(ValueError):self.op('chat_acao',id=cid,acao='mover',destino=None)
                self.op('rascunho',id=cid,texto='Proxima pergunta')
            finally:liberar.set()
            s=self.esperar(lambda s:not s['ocupado'])
            self.assertEqual(len(s['mensagens']),2);self.assertEqual(s['conversa']['rascunho'],'Proxima pergunta')
            self.assertEqual(api.call_args.kwargs['historico'],[])
            self.assertEqual(api.call_args.kwargs['caderno']['id'],bid)
        self.assertEqual(self.op('navegar',conversa=outro)['mensagens'],[])

    def test_falha_ia_preserva_pergunta_e_mensagem_de_erro(self):
        cid=self.chat()
        with patch('tutor_calculo.servico.perguntar',side_effect=RuntimeError('Falha simulada')):
            self.op('enviar',id=cid,texto='Minha pergunta',modo='Corrigir')
            s=self.esperar(lambda s:not s['ocupado'])
        self.assertEqual(s['conversa']['rascunho'],'Minha pergunta')
        self.assertEqual(s['mensagens'][-1]['estado'],'erro')
        self.assertEqual(s['mensagens'][0]['texto'],'Minha pergunta')

    def test_falha_processamento_e_recuperacao_ao_reabrir(self):
        cid=self.chat();arq=self.pasta/'invalid.pdf';arq.write_bytes(b'invalid')
        self.app.importar([str(arq)]);s=self.esperar(lambda s:s['anexos'] and s['anexos'][0]['estado']=='erro')
        mid=s['anexos'][0]['id']
        with self.assertRaises(ValueError):self.op('material_acao',id=mid,acao='selecionar',valor=True)
        with HistoricoFechado(self.app.caminho) as h:
            with h.db:h.db.execute("UPDATE materiais SET estado='processando' WHERE id=?",(mid,))
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.app.caminho)
        self.assertEqual(self.op('estado')['anexos'][0]['estado'],'erro')

    def test_arquivados_permanecem_legiveis_sem_envio(self):
        bid=self.op('caderno_salvar',nome='Arquivado')['navegacao']['caderno_id'];cid=self.chat(bid)
        self.op('rascunho',id=cid,texto='Preservado')
        self.op('caderno_acao',id=bid,acao='arquivar',valor=True)
        with self.assertRaises(ValueError):self.op('enviar',id=cid,texto='Teste',modo='Explicar')
        self.assertEqual(self.op('estado')['conversa']['rascunho'],'Preservado')
        self.op('caderno_acao',id=bid,acao='arquivar',valor=False)
        self.op('chat_acao',id=cid,acao='arquivar',valor=True)
        self.op('navegar',conversa=cid)
        with self.assertRaises(ValueError):self.op('rascunho',id=cid,texto='Alteracao')

    def test_configurar_nao_faz_consulta_nem_devolve_chave(self):
        with patch('tutor_calculo.servico.salvar_configuracao') as salvar,patch('tutor_calculo.servico.perguntar') as ia:
            resultado=self.op('configurar',provedor='openai',chave='nova-chave',modelo='teste')
            salvar.assert_called_once_with('nova-chave','teste','openai');ia.assert_not_called()
            self.assertNotIn('nova-chave',json.dumps(resultado))


class HistoricoFechado:
    def __init__(self,p):self.p=p
    def __enter__(self):self.h=Historico(self.p);return self.h
    def __exit__(self,*args):self.h.fechar()

if __name__=='__main__':unittest.main()
