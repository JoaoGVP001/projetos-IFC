"""Aceites L4 com dados fictícios; nenhum consumo de API online."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from tutor_calculo.servico import Aplicacao
from tutor_calculo.armazenamento import Historico
from tutor_calculo.paginas import nova,validar,Paginas
from tutor_calculo.paginas_servico import exportar_worker
from tutor_calculo.provedores.contratos import Cancelamento,ConsultaCancelada


class PaginasTest(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.root=Path(self.tmp.name);self.path=self.root/'h.sqlite3';self.app=Aplicacao(self.path);self.addCleanup(self.cleanup)
        self.pid=self.app.executar('pagina_criar',{'caderno':None})['id']
    def cleanup(self):self.app.fechar();self.app._executor.shutdown(wait=True);self.tmp.cleanup()
    def edit(self,content):
        p=self.app.executar('pagina_obter',{'id':self.pid});return self.app.executar('pagina_rascunho',{'id':self.pid,'conteudo':content,'revisao':p['revisao']})
    def wait(self,jid):
        for _ in range(200):
            j=self.app.executar('pagina_job',{'id':jid})
            if j['estado']!='executando':return j
            time.sleep(.025)
        self.fail('Tarefa não concluiu.')
    def test_rascunho_versoes_reinicio_conflito_busca_arquivo(self):
        content=nova('Derivadas');content['assunto']='Cálculo';content['secoes'][0]['texto']='Taxa de variação $f(x)=x^2$.';p=self.edit(content)
        self.app.executar('pagina_salvar',{'id':self.pid});original=self.app.executar('pagina_versao',{'id':self.pid,'versao':1})
        old_revision=p['revisao'];content['secoes'][0]['texto']='Texto revisado';self.edit(content)
        with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('pagina_rascunho',{'id':self.pid,'conteudo':content,'revisao':old_revision})
        self.assertEqual(self.app.executar('pagina_versao',{'id':self.pid,'versao':1}),original)
        self.assertEqual(self.app.executar('paginas',{'caderno':None,'busca':'REVISADO'})['total'],1)
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        self.assertEqual(self.app.executar('pagina_obter',{'id':self.pid})['rascunho']['secoes'][0]['texto'],'Texto revisado')
        p=self.app.executar('pagina_obter',{'id':self.pid});self.app.executar('pagina_acao',{'id':self.pid,'acao':'restaurar_versao','versao':1,'revisao':p['revisao']})
        self.assertEqual(self.app.executar('pagina_obter',{'id':self.pid})['rascunho'],original['conteudo'])
        self.app.executar('pagina_acao',{'id':self.pid,'acao':'arquivar','valor':True})
        with self.assertRaises(ValueError):self.edit(content)
        self.assertEqual(self.app.executar('paginas',{'caderno':None,'arquivadas':True})['total'],1)
        self.app.executar('pagina_acao',{'id':self.pid,'acao':'arquivar','valor':False})
        copy=self.app.executar('pagina_acao',{'id':self.pid,'acao':'duplicar'});self.assertNotEqual(copy['id'],self.pid)
    def test_limites_html_codigo_recurso_nao_autorizado(self):
        for change in ({'titulo':''},{'secoes':[]},{'fundo':'script'}):
            with self.assertRaises(ValueError):validar({**nova(),**change})
        for value in ('<script>alert(1)</script>','![x](file:///tmp/segredo)'):
            c=nova();c['secoes'][0]['texto']=value
            with self.assertRaises(ValueError):validar(c)
        c=nova();c['secoes'][0]['recurso']='../../segredo'
        with self.assertRaises(ValueError):validar(c)
        c=nova();c['secoes'][0]['origem']='ferramenta'
        with self.assertRaises(ValueError):validar(c)
        math=nova();math['secoes'][0]['texto']='$x<y>z$';self.assertEqual(validar(math)['secoes'][0]['texto'],'$x<y>z$')
        c=nova();c['secoes'][0]['texto']='```python\n__import__("os")\n```';self.assertEqual(validar(c)['secoes'][0]['texto'],c['secoes'][0]['texto'])
    def test_calculo_congelado_origem_removida_tipo_e_comentarios(self):
        cid=self.app.executar('chat_criar',{})['conversa']['id'];j=self.app.executar('discreta_executar',{'conversa':cid,'spec':{'tipo':'relacoes','sobre':True,'A':'{1,2,3}','R':'{(1,2),(2,3)}'}})['id']
        for _ in range(200):
            r=self.app.executar('discreta_obter',{'id':j})
            if r['estado']!='executando':break
            time.sleep(.025)
        p=self.app.executar('pagina_calculo',{'id':self.pid,'calculo':j});rid=p['rascunho']['secoes'][-1]['recurso'];self.assertIn('transitiva',p['render']['recursos'][rid]['resumo'])
        self.app.executar('pagina_salvar',{'id':self.pid});original=self.app.executar('pagina_versao',{'id':self.pid,'versao':1})
        c=p['rascunho'];c['secoes'][-1]['texto']='Nota do usuário';changed=self.edit(c);self.assertEqual(changed['rascunho']['secoes'][-1]['origem'],'usuario')
        self.app.executar('chat_acao',{'id':cid,'acao':'excluir','confirmado':True})
        after=self.app.executar('pagina_obter',{'id':self.pid});self.assertTrue(after['render']['avisos']);self.assertEqual(after['render']['recursos'][rid]['imagem'],original['recursos'][rid]['imagem'])
        self.assertEqual(self.app.executar('pagina_versao',{'id':self.pid,'versao':1}),original)
        with self.app._banco() as (h,c,b):
            raw=h.db.execute('SELECT documento FROM pagina_versoes WHERE pagina_id=?',(self.pid,)).fetchone()[0]
            self.assertNotIn('data:image',raw)
    def test_mensagem_preview_chat_e_imagem_externa_nao_e_importada(self):
        cid=self.app.executar('chat_criar',{})['conversa']['id']
        with self.app._banco() as (h,c,b):h.adicionar(cid,'assistant','Uma resposta escolhida para estudo.','ok','ollama','modelo')
        mid=self.app.executar('estado',{})['mensagens'][-1]['id']
        page=self.app.executar('pagina_criar',{'caderno':None,'mensagem':mid})
        refs=self.app.executar('estado',{})['paginas_chat'];self.assertEqual(refs[0]['id'],page['id']);self.assertEqual(refs[0]['mensagem'],mid)
        self.assertEqual(page['rascunho']['secoes'][0]['origem'],'ia')
        # Não interpretar imagens Markdown externas de uma mensagem como anexos confiáveis.
        with self.app._banco() as (h,c,b):h.adicionar(cid,'user','![x](file:///tmp/arquivo)')
        mid=self.app.executar('estado',{})['mensagens'][-1]['id']
        with self.assertRaises(ValueError):self.app.executar('pagina_criar',{'caderno':None,'mensagem':mid})

    def test_questao_gabarito_oculto_e_snapshot_nao_alterado(self):
        a=self.app.executar('atividade_salvar',{'caderno':None,'conteudo':{'titulo':'Relações','exercicios':[{'id':'q1','formato':'vf','enunciado':'R é transitiva?','resposta':False,'explicacao':'Falta (1,3).'}]}})
        t=self.app.executar('tentativa_iniciar',{'atividade':a['id']})
        with self.app._banco() as (h,c,b):before=h.db.execute('SELECT snapshot,respostas FROM tentativas WHERE id=?',(t['id'],)).fetchone();before=tuple(before)
        p=self.app.executar('pagina_questao',{'tentativa':t['id'],'questao':'q1','solucao':False});self.assertNotIn('Falta (1,3)',json.dumps(p))
        with self.assertRaisesRegex(ValueError,'Revele'):self.app.executar('pagina_questao',{'tentativa':t['id'],'questao':'q1','solucao':True})
        with self.app._banco() as (h,c,b):self.assertEqual(tuple(h.db.execute('SELECT snapshot,respostas FROM tentativas WHERE id=?',(t['id'],)).fetchone()),before)
        self.app.executar('tentativa_revelar',{'id':t['id'],'exercicio':'q1'});p=self.app.executar('pagina_questao',{'tentativa':t['id'],'questao':'q1','solucao':True});self.assertIn('Falta (1,3)',json.dumps(p))
    def test_biblioteca_deduplicada_sem_selecao_e_proveniencia(self):
        c=nova('Revisão de lógica');c['secoes'][0]['texto']='Uma explicação da IA para $p -> q$.';c['secoes'][0]['origem']='ia';self.edit(c);self.app.executar('pagina_salvar',{'id':self.pid})
        r=self.app.executar('pagina_material',{'id':self.pid,'versao':1,'revisada':True});second=self.app.executar('pagina_material',{'id':self.pid,'versao':1,'revisada':True});self.assertEqual(r['material'],second['material']);self.assertFalse(second['novo'])
        cid=self.app.executar('chat_criar',{})['conversa']['id']
        with self.app._banco() as (h,c,b):
            self.assertEqual(b.anexos(cid),[]);b.vincular(r['material'],cid,True);fontes=b.recuperar(cid,'explicação lógica');self.assertTrue(fontes);from tutor_calculo.materiais import contexto_documental
            self.assertIn('sem verificação global',contexto_documental(fontes))
    def test_propostas_tres_provedores_explicitamente_aplicadas(self):
        content=nova('Lógica');content['secoes'][0]['texto']='Explique $p -> q$.';self.edit(content);row=self.app.executar('pagina_obter',{'id':self.pid})
        raw={'titulo':'Implicação','assunto':'Lógica','secoes':[{'id':'s1','titulo':'Resumo','texto':'Uma proposta revisável.','recurso':None}]}
        for provider in ('ollama','gemini','openai'):
            self.app._ia_preferencias.salvar(provider)
            with patch('tutor_calculo.ia.configuracao',return_value=('simulada','modelo')),patch('tutor_calculo.ia.perguntar',return_value=json.dumps(raw)):
                j=self.app.executar('pagina_previa',{'id':self.pid,'secoes':[row['rascunho']['secoes'][0]['id']],'materiais':[]});self.assertFalse(j['previa']['originais_enviados']);self.app.executar('pagina_consultar',{'id':j['id']});result=self.wait(j['id'])
            self.assertEqual(result['estado'],'concluida');self.assertEqual(self.app.executar('pagina_obter',{'id':self.pid})['rascunho'],row['rascunho'])
        accepted=self.app.executar('pagina_aceitar',{'id':self.pid,'trabalho':j['id']});self.assertEqual(accepted['rascunho']['titulo'],'Implicação');self.assertEqual(accepted['versao'],0)
        self.assertEqual(accepted['rascunho']['secoes'][0]['origem'],'ia')
    def test_proposta_invalida_conflito_e_provedor_alterado(self):
        row=self.app.executar('pagina_obter',{'id':self.pid});sid=row['rascunho']['secoes'][0]['id']
        j=self.app.executar('pagina_previa',{'id':self.pid,'secoes':[sid]});self.app._ia_preferencias.salvar('ollama')
        if j['previa']['selecao']['provedor']!='ollama':
            with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('pagina_consultar',{'id':j['id']})
        for raw in ('não JSON',json.dumps({'titulo':'X','assunto':'','secoes':[{'id':'s','titulo':'','texto':'','recurso':'inventado'}]})):
            with patch('tutor_calculo.ia.perguntar',return_value=raw):
                j=self.app.executar('pagina_previa',{'id':self.pid,'secoes':[sid]});self.app.executar('pagina_consultar',{'id':j['id']});self.assertEqual(self.wait(j['id'])['estado'],'erro')
        j=self.app.executar('pagina_previa',{'id':self.pid,'secoes':[sid]});c=row['rascunho'];c['titulo']='Editado';self.edit(c)
        with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('pagina_consultar',{'id':j['id']})
    def test_exportacao_versao_fixa_cancelamento_recuperacao_integridade(self):
        self.app.executar('pagina_salvar',{'id':self.pid});captured=[]
        def fake(doc,dest,token):
            captured.append(doc);raw=b'%PDF-dados-ficticios';(dest/'pagina.pdf').write_bytes(raw)
            return {'folhas':1,'avisos':[],'runtime':'simulado','arquivos':[{'nome':'pagina.pdf','tamanho':len(raw),'hash':sha256(raw).hexdigest()}]}
        with patch('tutor_calculo.paginas_servico.exportar_worker',side_effect=fake):
            j=self.app.executar('pagina_exportar',{'id':self.pid,'versao':1});self.assertEqual(self.wait(j['id'])['estado'],'concluida')
        c=nova('Outro rascunho');self.edit(c);self.assertEqual(captured[0]['conteudo']['titulo'],'Nova página')
        self.assertEqual(len(self.app._paginas.arquivos(j['id'],'pdf')),1)
        self.assertEqual(self.app.executar('pagina_exportar',{'id':self.pid,'versao':1})['id'],j['id'])
        def canceled(doc,dest,token):token.cancelar();token.verificar()
        with patch('tutor_calculo.paginas_servico.exportar_worker',side_effect=canceled):
            cjob=self.app.executar('pagina_exportar',{'id':self.pid,'versao':1,'refazer':True});self.assertEqual(self.wait(cjob['id'])['estado'],'cancelada')
        self.assertFalse((self.app._paginas.exportacoes/cjob['id']).exists())
        (self.app._paginas.exportacoes/j['id']/'pagina.pdf').write_bytes(b'alterado')
        with self.assertRaises(ValueError):self.app._paginas.arquivos(j['id'],'pdf')
        with self.app._banco() as (h,c,b),h.db:h.db.execute("UPDATE pagina_jobs SET estado='executando' WHERE id=?",(cjob['id'],))
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path);self.assertEqual(self.app.executar('pagina_job',{'id':cjob['id']})['estado'],'interrompida')
    def test_worker_pre_cancelado_e_timeout(self):
        token=Cancelamento();token.cancelar()
        with self.assertRaises(ConsultaCancelada):exportar_worker({},self.root,token)
        with self.assertRaisesRegex(RuntimeError,'tempo'):exportar_worker({},self.root,Cancelamento(),timeout=.00001)
    def test_migracao_v10_rollback_preserva_tabelas_anteriores(self):
        self.app.fechar();self.app._executor.shutdown(wait=True)
        with sqlite3.connect(self.path) as db:
            for table in ('pagina_materiais','pagina_jobs','pagina_navegacao','pagina_versoes','paginas_estudo','pagina_recursos'):db.execute('DROP TABLE '+table)
            db.execute('PRAGMA user_version=10');before=db.execute('SELECT * FROM estudo_navegacao').fetchall()
        def fail(db):db.execute('CREATE TABLE parcial(id)');raise RuntimeError('simulado')
        with patch('tutor_calculo.paginas.migrar_paginas',side_effect=fail),self.assertRaises(RuntimeError):Historico(self.path)
        with sqlite3.connect(self.path) as db:self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],10);self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='parcial'").fetchone())
        self.app=Aplicacao(self.path)
        with self.app._banco() as (h,c,b):self.assertEqual(h.db.execute('SELECT * FROM estudo_navegacao').fetchall()[0][:],before[0]);self.assertEqual(h.db.execute('pragma foreign_key_check').fetchall(),[])
        self.assertTrue(Path(str(self.path)+'.v10.backup').exists())

if __name__=='__main__':unittest.main()
