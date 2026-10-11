import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy
from tutor_calculo.armazenamento import Historico
from tutor_calculo.atividades import Atividades, validar_conteudo
from tutor_calculo.tentativas import Tentativas
from tutor_calculo.cadernos import Cadernos
from tutor_calculo.servico import Aplicacao
from tutor_calculo.materiais import Biblioteca, Extracao


def conteudo():
    return {'titulo':'Revisão de funções', 'assuntos':'Funções', 'dificuldade':'basica', 'exercicios':[
        {'id':'q1', 'formato':'escolha', 'enunciado':'$2+2=?$', 'alternativas':[{'id':'a','texto':'3'},{'id':'b','texto':'4'}], 'resposta':'b','explicacao':'Some dois e dois.'},
        {'id':'q2', 'formato':'vf', 'enunciado':'$0$ é par.', 'resposta':True},
        {'id':'q3', 'formato':'numerica', 'enunciado':'Aproxime $\\sqrt{2}$.', 'resposta':'1.414', 'tolerancia':'0.001'},
        {'id':'q4', 'formato':'aberta', 'enunciado':'Explique função.'}]}


class EstudoTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'h.sqlite3'; self.h=Historico(self.path)
        self.a=Atividades(self.h); self.t=Tentativas(self.h); self.c=Cadernos(self.h); self.book=self.c.listar()[0]['id']
    def tearDown(self): self.h.fechar(); self.tmp.cleanup()
    def criar(self, **d): return self.a.salvar({'conteudo':conteudo(), 'caderno':self.book, **d})
    def responder(self, t, q, resposta, pos=0): return self.t.salvar({'id':t['id'],'exercicio':q,'resposta':resposta,'posicao':pos})

    def test_migracao_backup_preserva_v5(self):
        cid=self.h.criar(); self.h.adicionar(cid,'user','preservar'); self.h.rascunho(cid,'rascunho'); self.h.fechar()
        with sqlite3.connect(self.path) as db:
            for tabela in ['estudo_navegacao','atividade_jobs','tentativas','atividade_versoes','atividades']: db.execute('DROP TABLE '+tabela)
            db.execute('PRAGMA user_version=5')
        self.h=Historico(self.path)
        self.assertEqual(self.h.db.execute('PRAGMA user_version').fetchone()[0],6)
        self.assertEqual(self.h.obter(cid)['rascunho'],'rascunho'); self.assertEqual(self.h.mensagens(cid)[0]['texto'],'preservar')
        with sqlite3.connect(str(self.path)+'.v5.backup') as db: self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],5)
    def test_rollback_ddl(self):
        self.h.fechar()
        with sqlite3.connect(self.path) as db:
            for tabela in ['estudo_navegacao','atividade_jobs','tentativas','atividade_versoes','atividades']: db.execute('DROP TABLE '+tabela)
            db.execute('PRAGMA user_version=5')
        def falha(db): db.execute('CREATE TABLE parcial(id)'); raise RuntimeError('simulada')
        with patch('tutor_calculo.atividades.migrar_atividades',side_effect=falha), self.assertRaises(RuntimeError): Historico(self.path)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],5); self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='parcial'").fetchone())
        self.h=Historico(self.path)
    def test_validacao_formatos(self):
        for mutate in [lambda d:d.update(exercicios=[]),lambda d:d['exercicios'][0].update(enunciado=''),lambda d:d['exercicios'][0].update(formato='x'),
                       lambda d:d['exercicios'][0].update(resposta='z'),lambda d:d['exercicios'][0]['alternativas'][0].update(texto='4'),
                       lambda d:d['exercicios'][1].update(resposta='false'),lambda d:d['exercicios'][2].update(resposta='NaN'),
                       lambda d:d['exercicios'][2].update(tolerancia='-1'),lambda d:d['exercicios'][2].update(resposta='sqrt(2)'),
                       lambda d:d['exercicios'][3].update(id='q1')]:
            d=conteudo(); mutate(d)
            with self.subTest(d=d),self.assertRaises(ValueError): validar_conteudo(d)
    def test_correcao_formatos_e_contagens(self):
        t=self.t.iniciar(self.criar()['id']); self.responder(t,'q1','b');self.responder(t,'q2',False);self.responder(t,'q3','1,415');self.responder(t,'q4','Definição')
        r=self.t.finalizar(t['id']); self.assertEqual(r['resumo']['objetivas'],3);self.assertEqual(r['resumo']['acertos'],2);self.assertEqual(r['resumo']['erros'],1)
        self.assertEqual(r['resultado']['q4']['estado'],'sem_gabarito');self.assertEqual(r['resumo']['nao_avaliadas'],1)
    def test_sem_resposta_nao_e_zero(self):
        t=self.t.iniciar(self.criar()['id'])
        with self.assertRaises(ValueError): self.t.finalizar(t['id'])
        r=self.t.finalizar(t['id'],True);self.assertEqual(r['resumo']['erros'],0);self.assertEqual(r['resumo']['objetivas'],0);self.assertEqual(r['resumo']['nao_avaliadas'],4)
    def test_numero_invalido_revisao(self):
        t=self.t.iniciar(self.criar()['id']);self.responder(t,'q3','1/2');r=self.t.finalizar(t['id'],True)
        self.assertEqual(r['resultado']['q3']['estado'],'revisao_necessaria');self.assertEqual(r['resumo']['erros'],0)
    def test_tolerancia_zero_e_limite(self):
        d=conteudo(); d['exercicios'][2].update(resposta='1e100',tolerancia='0');t=self.t.iniciar(self.criar(conteudo=d)['id']);self.responder(t,'q3','9.9999999999999999999999999999e99')
        r=self.t.finalizar(t['id'],True);self.assertEqual(r['resultado']['q3']['estado'],'incorreta')
    def test_rascunho_reinicio_e_gabarito_oculto(self):
        t=self.t.iniciar(self.criar()['id']);self.responder(t,'q2',False,1);self.h.fechar();self.h=Historico(self.path);self.t=Tentativas(self.h)
        r=self.t.obter(t['id']);self.assertEqual(r['posicao'],1);self.assertIs(r['respostas']['q2']['resposta'],False)
        self.assertNotIn('resposta',r['snapshot']['conteudo']['exercicios'][0]);r=self.t.revelar(t['id'],'q1');self.assertEqual(r['snapshot']['conteudo']['exercicios'][0]['resposta'],'b');self.assertEqual(r['resumo']['solucoes'],1)
    def test_finalizacao_idempotente_e_immutavel(self):
        a=self.criar();t=self.t.iniciar(a['id']);self.responder(t,'q1','b');r=self.t.finalizar(t['id'],True)
        self.assertEqual(self.t.finalizar(t['id'])['fim'],r['fim']);self.assertEqual(len(self.t.historico(a['id'])),1)
        with self.assertRaises(ValueError): self.responder(t,'q1','a')
    def test_edicao_snapshot_desde_inicio(self):
        a=self.criar();t=self.t.iniciar(a['id']);d=conteudo();d['exercicios'][0]['resposta']='a';self.a.salvar({'id':a['id'],'versao':1,'conteudo':d,'caderno':self.book})
        self.responder(t,'q1','b');r=self.t.finalizar(t['id'],True);self.assertEqual(r['resultado']['q1']['estado'],'correta');self.assertEqual(r['versao'],1)
        nova=self.t.iniciar(a['id'],True);self.assertEqual(nova['versao'],2);self.assertFalse(self.t.comparar([t['id'],nova['id']])['mesma_versao'])
    def test_nova_tentativa_e_comparacao(self):
        a=self.criar();t=self.t.iniciar(a['id']);self.assertEqual(self.t.iniciar(a['id'])['id'],t['id']);nova=self.t.iniciar(a['id'],True)
        self.assertNotEqual(t['id'],nova['id']);self.assertTrue(self.t.comparar([t['id'],nova['id']])['mesma_versao'])
    def test_revisao_manual_separada(self):
        t=self.t.iniciar(self.criar()['id']);self.responder(t,'q4','Minha definição');self.t.finalizar(t['id'],True)
        r=self.t.revisar({'id':t['id'],'exercicio':'q4','texto':'Rever domínio','avaliacao':'revisar'});self.assertEqual(r['resumo']['objetivas'],0);self.assertEqual(r['respostas']['q4']['revisao']['texto'],'Rever domínio')
    def test_caderno_chat_excluido_preserva(self):
        cid=self.h.criar(self.book);a=self.criar(origem_chat=cid);t=self.t.iniciar(a['id']);self.h.excluir(cid);self.c.excluir(self.book)
        a=self.a.obter(a['id']);self.assertIsNone(a['caderno_id']);self.assertFalse(a['origem_disponivel']);self.assertEqual(self.t.obter(t['id'])['snapshot']['caderno'],'Preliminares de Matemática')
    def test_arquivo_move_dup_busca_isolamento(self):
        a=self.criar();self.assertEqual(self.a.listar({'caderno':None})['total'],0);self.assertEqual(self.a.listar({'caderno':self.book,'busca':'FUNÇÕES','formato':'vf'})['total'],1)
        dup=self.a.acao({'id':a['id'],'acao':'duplicar'});self.assertNotEqual(dup['id'],a['id'])
        self.a.acao({'id':a['id'],'acao':'mover','destino':None});self.a.acao({'id':a['id'],'acao':'arquivar','valor':True})
        with self.assertRaises(ValueError): self.t.iniciar(a['id'])
        self.assertEqual(self.a.listar({'caderno':None,'situacao':'arquivadas'})['total'],1)
        self.a.acao({'id':a['id'],'acao':'arquivar','valor':False});self.c.arquivar(self.book)
        self.assertTrue(self.a.obter(dup['id'])['caderno_arquivado'])
        with self.assertRaises(ValueError): self.t.iniciar(dup['id'])
    def test_edicao_concorrente_recusada(self):
        a=self.criar();self.a.salvar({'id':a['id'],'versao':1,'caderno':self.book,'conteudo':conteudo()})
        with self.assertRaises(ValueError):self.a.salvar({'id':a['id'],'versao':1,'caderno':self.book,'conteudo':conteudo()})
    def test_exercicio_alheio_rejeitado(self):
        t=self.t.iniciar(self.criar()['id'])
        with self.assertRaises(ValueError):self.responder(t,'outra','texto')
        with self.assertRaises(ValueError):self.responder(t,'q1','inexistente')
    def test_ajuda_isola_chat(self):
        outro=self.h.criar();self.h.adicionar(outro,'user','SEGREDO OUTRA CONVERSA');t=self.t.iniciar(self.criar()['id']);cid=self.t.ajuda_chat(t['id'],'q1')
        draft=self.h.obter(cid)['rascunho'];self.assertIn('2+2',draft);self.assertNotIn('SEGREDO',draft);self.assertNotIn('q2',draft);self.assertNotIn('resposta_esperada',draft)
    def test_fontes_removidas_preservam_referencia(self):
        cid=self.h.criar();p=Path(self.tmp.name)/'fonte.txt';p.write_text('Função relaciona domínio e imagem.');b=Biblioteca(self.h);mid,_=b.adicionar_arquivo(p,cid);b.salvar_extracao(mid,Extracao([(1,p.read_text())],'pronto',''))
        d=conteudo();d['exercicios'][0]['referencias']=[{'material_id':mid,'pagina':1}];a=self.criar(conteudo=d,materiais=[mid]);t=self.t.iniciar(a['id']);b.excluir(mid)
        self.assertFalse(self.a.obter(a['id'])['fontes'][0]['disponivel']);self.assertFalse(self.t.obter(t['id'])['snapshot']['fontes'][0]['disponivel'])

    def test_leitura_arquivada_posicao_preservada(self):
        a=self.criar();t=self.t.iniciar(a['id']);self.c.arquivar(self.book)
        r=self.t.navegar({'id':t['id'],'posicao':3});self.assertEqual(r['posicao'],3);self.assertFalse(r['editavel'])
        with self.assertRaises(ValueError):self.responder(t,'q4','alteração')
    def test_comparacao_isola_atividades(self):
        t=self.t.iniciar(self.criar()['id']);outro=self.t.iniciar(self.criar()['id'])
        with self.assertRaises(ValueError):self.t.comparar([t['id'],outro['id']])
    def test_migracao_v5_preserva_indices_materiais_selecao(self):
        cid=self.h.criar(self.book);p=Path(self.tmp.name)/'fonte.txt';p.write_text('Conteúdo de derivadas.');b=Biblioteca(self.h);mid,_=b.adicionar_arquivo(p,cid);b.salvar_extracao(mid,Extracao([(1,p.read_text())],'pronto',''));b.vincular(mid,cid,True)
        tabelas=['conversas','mensagens','cadernos','navegacao','materiais','chat_materiais','materiais_cadernos','paginas','trechos','trechos_fts']
        antes={k:[tuple(r) for r in self.h.db.execute('SELECT * FROM '+k)] for k in tabelas};self.h.fechar()
        with sqlite3.connect(self.path) as db:
            for tabela in ['estudo_navegacao','atividade_jobs','tentativas','atividade_versoes','atividades']:db.execute('DROP TABLE '+tabela)
            db.execute('PRAGMA user_version=5')
        self.h=Historico(self.path)
        self.assertEqual(antes,{k:[tuple(r) for r in self.h.db.execute('SELECT * FROM '+k)] for k in tabelas})
        self.assertTrue(Biblioteca(self.h).listar('derivadas'))


class IATest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'h.sqlite3';self.app=Aplicacao(self.path)
        self.cfg=patch('tutor_calculo.estudo.configuracao',return_value=('fake','modelo-fake'));self.prov=patch('tutor_calculo.estudo.provedor_ativo',return_value='gemini');self.cfg.start();self.prov.start()
    def tearDown(self):self.app._executor.shutdown(wait=True);self.app.fechar();self.cfg.stop();self.prov.stop();self.tmp.cleanup()
    def op(self,op,**d):return self.app.executar(op,d)
    def aguardar(self,jid):
        for _ in range(100):
            j=self.op('estudo_job',id=jid)
            if j['estado']!='executando':return j
            time.sleep(.01)
        self.fail('Timeout')
    def previa(self,**d):return self.op('estudo_previa',tipo='geracao',assunto='Funções',quantidade=4,formatos=['aberta','vf','numerica','escolha'],**d)
    def test_proposta_validada_editavel_e_nao_salva_automaticamente(self):
        j=self.previa();self.assertEqual(j['previa']['fontes'],[])
        with patch('tutor_calculo.estudo.perguntar',return_value=json.dumps(conteudo())) as mock:
            self.op('estudo_consultar',id=j['id']);done=self.aguardar(j['id']);self.assertEqual(done['estado'],'concluida');self.assertEqual(mock.call_args.kwargs['provedor'],'gemini')
        self.assertEqual(self.op('atividades')['total'],0);a=self.op('atividade_salvar',conteudo=done['resultado'],proposta=j['id']);self.assertEqual(a['origem'],'ia')
        self.assertEqual(self.op('estudo_consultar',id=j['id'])['estado'],'concluida')
    def test_json_invalido_e_api_falha_nao_criam_atividades(self):
        for answer in ['texto comum',json.dumps({'titulo':'sem questões'}),json.dumps({'titulo':'x','exercicios':[{'enunciado':'x','formato':'inexistente'}]})]:
            j=self.previa()
            with patch('tutor_calculo.estudo.perguntar',return_value=answer):self.op('estudo_consultar',id=j['id']);self.assertEqual(self.aguardar(j['id'])['estado'],'erro')
        j=self.previa()
        with patch('tutor_calculo.estudo.perguntar',side_effect=RuntimeError('Sem créditos')):self.op('estudo_consultar',id=j['id']);self.assertIn('Sem créditos',self.aguardar(j['id'])['erro'])
        self.assertEqual(self.op('atividades')['total'],0)
    def test_fontes_explicitas_sem_mudar_selecao_chat(self):
        with self.app._banco() as (h,c,b):
            cid=h.criar();p=Path(self.tmp.name)/'m.txt';p.write_text('Funções: domínio e imagem.');mid,_=b.adicionar_arquivo(p,cid);b.salvar_extracao(mid,Extracao([(1,p.read_text())],'pronto',''))
            b.vincular(mid,cid,True)
        self.assertFalse(self.previa()['previa']['fontes']);j=self.previa(materiais=[mid]);self.assertEqual(j['previa']['fontes'][0]['material_id'],mid)
        from tutor_calculo.materiais import contexto_documental
        self.assertEqual(json.loads(contexto_documental(j['previa']['fontes']))[0]['material_id'],mid)
        self.assertFalse(j['previa']['originais_enviados'])
        bad=conteudo();bad['exercicios'][0]['referencias']=[{'material_id':'inventada','pagina':3}]
        with patch('tutor_calculo.estudo.perguntar',return_value=json.dumps(bad)):self.op('estudo_consultar',id=j['id']);self.assertEqual(self.aguardar(j['id'])['estado'],'erro')
    def test_feedback_dica_e_metadata_sem_nota(self):
        a=self.op('atividade_salvar',conteudo=conteudo());t=self.op('tentativa_iniciar',atividade=a['id']);self.op('tentativa_salvar',id=t['id'],exercicio='q4',resposta='Relação',posicao=3)
        for tipo in ['dica','feedback']:
            j=self.op('estudo_previa',tipo=tipo,tentativa=t['id'],exercicio='q4')
            if tipo=='dica':self.assertNotIn('resposta_esperada',j['previa']['pedido'])
            with patch('tutor_calculo.estudo.perguntar',return_value='Confira o domínio.'):self.op('estudo_consultar',id=j['id']);self.assertEqual(self.aguardar(j['id'])['estado'],'concluida')
        r=self.op('tentativa_obter',id=t['id']);self.assertEqual(r['respostas']['q4']['feedbacks'][0]['modelo'],'modelo-fake');self.assertEqual(r['resumo']['dicas'],1)
        r=self.op('tentativa_finalizar',id=t['id'],confirmado=True);self.assertEqual(r['resumo']['erros'],0);self.assertEqual(r['resumo']['objetivas'],0)
    def test_interrupcao_recuperavel_e_navegacao(self):
        j=self.previa();self.op('estudo_navegar',area='atividades')
        with self.app._banco() as (h,c,b):
            with h.db:h.db.execute("UPDATE atividade_jobs SET estado='executando' WHERE id=?",(j['id'],))
        self.app.fechar();self.app=Aplicacao(self.path);self.assertEqual(self.op('estado')['estudo']['area'],'atividades');self.assertEqual(self.op('estudo_job',id=j['id'])['estado'],'erro')
    def test_preview_resposta_mudou_recusa(self):
        a=self.op('atividade_salvar',conteudo=conteudo());t=self.op('tentativa_iniciar',atividade=a['id']);self.op('tentativa_salvar',id=t['id'],exercicio='q4',resposta='A')
        j=self.op('estudo_previa',tipo='feedback',tentativa=t['id'],exercicio='q4');self.op('tentativa_salvar',id=t['id'],exercicio='q4',resposta='B')
        with self.assertRaises(ValueError):self.op('estudo_consultar',id=j['id'])

    def test_openai_explicitamente_preservado(self):
        with patch('tutor_calculo.estudo.provedor_ativo',return_value='openai'):
            j=self.previa()
            with patch('tutor_calculo.estudo.perguntar',return_value=json.dumps(conteudo())) as mock:
                self.op('estudo_consultar',id=j['id']);done=self.aguardar(j['id'])
                self.assertEqual(done['estado'],'concluida');self.assertEqual(mock.call_args.kwargs['provedor'],'openai');self.assertEqual(mock.call_args.kwargs['historico'] if 'historico' in mock.call_args.kwargs else None,None)
