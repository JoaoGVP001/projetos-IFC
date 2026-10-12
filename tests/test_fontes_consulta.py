"""Conferência dos trechos enviados, sem novas buscas/API ao ler o histórico."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch
from tutor_calculo.servico import Aplicacao
from tutor_calculo.fontes_consulta import digest
from tutor_calculo.referencia_estudo import casos


class FontesConsultaTest(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.root=Path(self.tmp.name);self.app=Aplicacao(self.root/'h.sqlite3');self.addCleanup(self.cleanup)
        self.cid=self.app.executar('chat_criar',{})['conversa']['id']
        with self.app._banco() as (h,c,b):
            f=self.root/'notas.txt';f.write_text('O mini-simulado tem sete questões e duração de 23 minutos. A figura não foi extraída.')
            self.mid,_=b.adicionar_arquivo(f,self.cid);b.processar(self.mid);b.vincular(self.mid,self.cid,True)
    def cleanup(self):self.app.fechar();self.app._executor.shutdown(wait=True);self.tmp.cleanup()
    def preview(self):return self.app.executar('previa',{'id':self.cid,'texto':'Quantas questões tem o mini-simulado?','modo':'Explicar'})
    def send(self,p=None,answer='O mini-simulado tem sete questões [M1].'):
        with patch('tutor_calculo.servico.perguntar',return_value=answer):
            d={'id':self.cid,'texto':'Quantas questões tem o mini-simulado?','modo':'Explicar'}
            if p:d['previa_token']=p['token']
            j=self.app.executar('enviar',d)['tarefa']
            for _ in range(300):
                with self.app._banco() as (h,c,b):r=h.db.execute('SELECT * FROM consultas_ia WHERE id=?',(j,)).fetchone()
                if r['estado']!='executando':return dict(r)
                time.sleep(.01)
            self.fail('Consulta não terminou.')
    def sources(self,r):return self.app.executar('consulta_fontes',{'mensagem':r['resposta_id']})
    def test_fluxo_sem_rebusca_snapshot_reinicio_pagina(self):
        p=self.preview();r=self.send(p);s=self.sources(r)
        self.assertEqual(s['fontes'][0]['texto'],p['fontes'][0]['texto']);self.assertTrue(s['envio_exato'])
        self.assertTrue(s['fontes'][0]['citada']);self.assertEqual(s['fontes'][0]['estado_atual'],'atual')
        self.assertEqual(s['fontes'][0]['hash_enviado'],digest(s['fontes'][0]['texto']))
        page=self.app.executar('pagina_criar',{'caderno':None,'mensagem':r['resposta_id']})
        self.assertEqual(page['render']['referencias'][0]['snapshot']['texto'],p['fontes'][0]['texto'])
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.root/'h.sqlite3')
        with patch('tutor_calculo.recuperacao.recuperar_chat',side_effect=AssertionError('Nova busca')),patch('tutor_calculo.servico.perguntar',side_effect=AssertionError('Nova consulta')):
            self.assertEqual(self.sources(r),s)
    def test_previa_rejeita_selecao_texto_caderno_modelo_e_timeout(self):
        p=self.preview()
        with self.app._banco() as (h,c,b):b.vincular(self.mid,self.cid,False)
        with self.assertRaisesRegex(ValueError,'mudou'):self.send(p)
        with self.app._banco() as (h,c,b):b.vincular(self.mid,self.cid,True)
        p=self.preview()
        with patch.object(self.app,'_selecao',return_value={'provedor':'outro'}):
            with self.assertRaisesRegex(ValueError,'mudou'):self.send(p)
        with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('enviar',{'id':self.cid,'texto':'Outra pergunta','modo':'Explicar','previa_token':p['token']})
        self.app._previas_estudo[p['token']]['tempo']-=601
        with self.assertRaisesRegex(ValueError,'expirada'):self.send(p)
    def test_extracao_alterada_recusa_envio_preserva_fonte_historica(self):
        p=self.preview();r=self.send(p);original=self.sources(r)['fontes'][0]['texto'];p=self.preview()
        with self.app._banco() as (h,c,b),h.db:h.db.execute('UPDATE paginas SET texto=? WHERE material_id=?',('Texto reprocessado, mudou.',self.mid))
        with self.assertRaisesRegex(ValueError,'mudou'):self.send(p)
        s=self.sources(r);self.assertEqual(s['fontes'][0]['estado_atual'],'alterado');self.assertEqual(s['fontes'][0]['texto'],original)
        with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('ia_ajuste_previa',{'id':r['id'],'acao':'curta'})
    def test_remocao_preserva_passado_nao_autoriza_reuso(self):
        r=self.send();saved=self.sources(r)
        with self.app._banco() as (h,c,b):b.excluir(self.mid)
        s=self.sources(r);self.assertEqual(s['fontes'][0]['texto'],saved['fontes'][0]['texto']);self.assertEqual(s['fontes'][0]['estado_atual'],'removido');self.assertFalse(s['fontes'][0]['original_disponivel'])
        with self.assertRaises(ValueError):self.app.executar('consulta_pagina',{'mensagem':r['resposta_id'],'referencia':'M1'})
    def test_referencia_verdadeira_nao_certifica_afirmacao_falsa(self):
        r=self.send(answer='São 40 minutos [M1].');s=self.sources(r)
        self.assertTrue(s['fontes'][0]['citada']);self.assertIn('não verificam',s['fontes'][0]['verificacao']);self.assertNotIn('aprovada',str(s))
    def test_abreviacao_local_snapshot_conserva_apenas_texto_enviado(self):
        self.app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','contexto':4096,'perfil':'rapido','escopo':'padrao'})
        with self.app._banco() as (h,c,b):
            f=self.root/'longa.txt';f.write_text('Mini-simulado: questões e minutos. '*400);mid,_=b.adicionar_arquivo(f,self.cid);b.processar(mid);b.vincular(mid,self.cid,True)
        p=self.preview();r=self.send(p);s=self.sources(r)
        self.assertEqual([f['texto'] for f in s['fontes']],[f['texto'] for f in p['fontes']])
        self.assertTrue(all(f['hash_enviado']==digest(f['texto']) for f in s['fontes']))
    def test_cliente_nao_altera_previa_guardada_no_servidor(self):
        p=self.preview();p['fontes'][0]['texto']='Conteúdo injetado';r=self.send(p)
        self.assertNotIn('injetado',self.sources(r)['fontes'][0]['texto'])
    def test_ferramenta_vinculada_sem_certificacao_global(self):
        r=self.send();calc=self.app.executar('discreta_executar',{'conversa':self.cid,'origem_mensagem':r['resposta_id'],'spec':{'tipo':'relacoes','sobre':True,'A':'{1,2,3}','R':'{(1,2),(2,3)}'}})
        for _ in range(300):
            j=self.app.executar('discreta_obter',{'id':calc['id']})
            if j['estado']!='executando':break
            time.sleep(.02)
        self.assertEqual(j['estado'],'concluida');self.assertEqual(j['previa']['origem_estudo']['mensagem'],r['resposta_id'])
        self.assertEqual(j['previa']['origem_estudo']['fontes'][0]['texto'],self.sources(r)['fontes'][0]['texto'])
        other=self.app.executar('chat_criar',{})['conversa']['id']
        with self.assertRaisesRegex(ValueError,'deste chat'):self.app.executar('math_executar',{'conversa':other,'origem_mensagem':r['resposta_id'],'spec':{'expressao':'x^2','inicio':'-1','fim':'1','operacoes':['grafico']}})
    def test_legado_sem_hash_recuperavel_e_hash_adulterado_recusado(self):
        r=self.send();snap=json.loads(r['snapshot']);s=self.sources(r)
        snap['preparada']['fontes'][0].pop('proveniencia');snap['preparada']['fontes'][0].pop('hash_enviado')
        with self.app._banco() as (h,c,b),h.db:h.db.execute('UPDATE consultas_ia SET snapshot=? WHERE id=?',(json.dumps(snap),r['id']))
        self.assertEqual(self.sources(r)['fontes'][0]['estado_atual'],'legado')
        snap=json.loads(r['snapshot']);snap['preparada']['fontes'][0]['texto']='Alterado'
        with self.app._banco() as (h,c,b),h.db:h.db.execute('UPDATE consultas_ia SET snapshot=? WHERE id=?',(json.dumps(snap),r['id']))
        self.assertEqual(self.sources(r)['fontes'][0]['estado_atual'],'invalido')
    def test_catalogo_30_casos_revisao_independente(self):
        c=casos();self.assertEqual(len(c),30)
        for area in ('calculo','discreta','documental'):self.assertEqual(sum(v['categoria']==area for v in c.values()),10)
        from tutor_calculo.avaliacao_local import avaliar
        self.assertEqual(avaliar('ref_discreta_quantificador','Algum k prova tudo.')['revisao_matematica'],'pendente')
        self.assertFalse(avaliar('ref_documental_contradicao','40 minutos [M1].')['checagens_pontuais'])
    def test_consulta_materiais_no_orcamento_sem_tarefa_de_aula(self):
        from tutor_calculo.ia import preparar_consulta
        f=casos()['ref_documental_ocr']['fontes']
        for contexto in (2048,4096):
            p=preparar_consulta('Qual a fórmula exata?',modo='Consultar materiais',fontes=f,provedor='ollama',local={'perfil':'rapido','contexto':contexto})
            budget=p['orcamento'];self.assertLessEqual(budget['entrada_estimada']+budget['reserva_saida']+budget['margem'],contexto)
            self.assertIn('ilegíveis permanecem desconhecidos',p['instrucoes']);self.assertNotIn('Termine resolução completa',p['instrucoes'])


if __name__=='__main__':unittest.main()
