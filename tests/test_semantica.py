"""Recuperação/persistência/isolamento com embeddings sintéticos, não benchmark de qualidade."""
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
from tutor_calculo.armazenamento import Historico
from tutor_calculo.materiais import Biblioteca,Extracao
from tutor_calculo.servico import Aplicacao
from tutor_calculo.semantica import (IndiceSemantico,Embeddings,MODELO,DIMENSAO,PERFIL,normalizar,decodificar)
from tutor_calculo.recuperacao import recuperar_chat,recuperar_estudo


class RuntimeEmbedding:
    def __init__(self):
        self.requests=[];self.calls=0;self.hold_after=None;self.release=threading.Event()
        self.started=threading.Event();self.digest='digest-modelo';self.remote=False;self.invalid=None
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def reply(self,data,status=200):
                self.send_response(status);self.end_headers()
                try:self.wfile.write(json.dumps(data).encode())
                except (BrokenPipeError,ConnectionResetError):pass
            def do_GET(self):
                if self.path=='/api/tags':self.reply({'models':[{'name':MODELO,'digest':owner.digest}]})
                else:self.reply({},404)
            def do_POST(self):
                data=json.loads(self.rfile.read(int(self.headers['Content-Length'])));owner.requests.append((self.path,data))
                if self.path=='/api/show':self.reply({'capabilities':['embedding'],**({'remote_host':'https://example.com'} if owner.remote else {})});return
                if self.path!='/api/embed':self.reply({},404);return
                owner.calls+=1
                if owner.hold_after and owner.calls>=owner.hold_after:owner.started.set();owner.release.wait(10)
                vectors=[]
                for text in data['input']:
                    v=[0.]*DIMENSAO;text=text.casefold()
                    v[0 if any(s in text for s in ('derivada','inclinação','curva','tangente')) else 1 if any(s in text for s in ('implicação','premissa','condicional')) else 2]=1.
                    if owner.invalid=='dimensao':v=v[:3]
                    if owner.invalid=='nan':v[0]=float('nan')
                    if owner.invalid=='zero':v=[0.]*DIMENSAO
                    vectors.append(v)
                self.reply({'model':MODELO,'embeddings':vectors})
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def close(self):self.release.set();self.server.shutdown();self.server.server_close()


class SemanticaTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'h.sqlite3'
        self.runtime=RuntimeEmbedding();self.app=Aplicacao(self.path)
    def tearDown(self):
        self.runtime.release.set();self.app.fechar();self.app._executor.shutdown(wait=True)
        self.runtime.close();self.temp.cleanup()
    def op(self,op,**dados):return self.app.executar(op,dados)
    def material(self,text='A derivada calcula a taxa instantânea de variação.',nome='apostila.pdf',bid=None,selected=True,pagina=8):
        with self.app._banco() as (h,c,b):
            cid=h.criar(bid);p=self.path.parent/nome;p.write_text(text)
            mid,_=b.adicionar_arquivo(p,cid);b.salvar_extracao(mid,Extracao([(pagina,text)],'pronto',metodo='PDF textual'))
            b.vincular(mid,cid,selected);c.salvar_navegacao(bid,cid)
            return cid,mid
    def indexar(self):
        self.op('semantica_indexar',url=self.runtime.url,confirmado=True)
        return self.esperar()
    def esperar(self):
        prazo=time.monotonic()+12
        while time.monotonic()<prazo:
            s=self.op('semantica_status')
            if s['trabalho']['estado']!='executando':return s
            time.sleep(.02)
        self.fail('Indexação não terminou.')
    def test_contrato_cpu_sem_chave_e_validacao(self):
        self.material()
        with patch('openai.OpenAI') as cloud,patch('tutor_calculo.gemini.consultar') as gemini:
            s=self.indexar();self.assertEqual(s['trabalho']['estado'],'concluido');cloud.assert_not_called();gemini.assert_not_called()
        data=next(data for endpoint,data in self.runtime.requests if endpoint=='/api/embed')
        self.assertEqual(data['options']['num_gpu'],0);self.assertEqual(data['keep_alive'],0)
        self.assertIs(data['truncate'],False);self.assertEqual(data['dimensions'],1024)
        self.assertNotIn('chave',data)
        for url in ('https://127.0.0.1:11434','http://example.com:11434','http://127.0.0.1:11434/api','http://u:p@127.0.0.1:11434'):
            with self.assertRaises(ValueError):Embeddings(url)
    def test_semantica_sem_termos_comuns_preserva_pagina_e_escopo(self):
        cid,mid=self.material();self.material('Uma implicação usa premissa e conclusão.',nome='segredo.pdf')
        self.indexar();report={}
        with self.app._banco() as (h,c,b):
            fs=recuperar_chat(b,cid,'inclinação tangente',report)
            self.assertEqual([f['material_id'] for f in fs],[mid]);self.assertEqual(fs[0]['pagina'],8)
            self.assertEqual(fs[0]['referencia'],'M1');self.assertEqual(report['metodo'],'busca híbrida local')
            self.assertEqual(report['indexados'],1)
            snippets,mats=recuperar_estudo(h,[mid],'inclinação tangente',False,{})
            self.assertEqual(snippets[0]['material_id'],mid);self.assertEqual(len(mats),1)
    def test_indexar_nao_autoriza_fontes_e_busca_caderno_filtrada(self):
        with self.app._banco() as (h,c,b):bid=c.criar('Cálculo')
        cid,mid=self.material(bid=bid,selected=False)
        self.material('A derivada secundária.',nome='outra.pdf')
        self.indexar()
        result=self.op('materiais',busca='inclinação tangente',modo='hibrida',caderno=bid)
        self.assertEqual([m['id'] for m in result['itens']],[mid]);self.assertTrue(result['itens'][0]['ocorrencias'])
        with self.app._banco() as (h,c,b):self.assertIsNone(self.app._fontes(h,b,cid,'inclinação tangente'))
    def test_inferencias_runtime_fora_de_escopo_nao_recebem_documentos(self):
        cid,mid=self.material();self.indexar();self.runtime.requests.clear()
        report={}
        with self.app._banco() as (h,c,b):recuperar_chat(b,cid,'inclinação tangente',report)
        inputs=[d['input'] for op,d in self.runtime.requests if op=='/api/embed']
        self.assertEqual(len(inputs),1);self.assertIn('Instruct:',inputs[0][0]);self.assertNotIn('A derivada',str(inputs))
    def test_incremental_sem_duplicar_e_reinicio(self):
        cid,mid=self.material();self.indexar();calls=self.runtime.calls
        self.indexar();self.assertEqual(self.runtime.calls,calls)
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        s=self.op('semantica_status');self.assertEqual(s['indexados'],1);self.assertEqual(s['habilitada'],1)
        with self.app._banco() as (h,c,b):self.assertTrue(recuperar_chat(b,cid,'inclinação tangente'))
    def test_cancelar_nao_publica_preparo_retoma(self):
        self.material('A derivada: '+('curva com inclinação variável. '*300))
        self.runtime.hold_after=2
        self.op('semantica_indexar',url=self.runtime.url,confirmado=True)
        self.assertTrue(self.runtime.started.wait(8));self.op('semantica_cancelar');s=self.esperar()
        self.assertEqual(s['trabalho']['estado'],'cancelado');self.assertEqual(s['indexados'],0)
        with self.app._banco() as (h,c,b):staged=h.db.execute('SELECT count(*) FROM semantica_preparo').fetchone()[0]
        self.assertEqual(staged,4)
        self.runtime.release.set();self.runtime.hold_after=None;calls=self.runtime.calls
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        s=self.indexar();self.assertEqual(s['indexados'],s['total']);self.assertGreater(self.runtime.calls,calls)
        self.assertLess(self.runtime.calls-calls,(s['total']+3)//4)
    def test_falha_reindexacao_preserva_indice_publicado(self):
        self.material();self.indexar();digest=self.op('semantica_status')['digest']
        self.runtime.digest='pesos-alterados';self.runtime.invalid='dimensao';status=self.indexar()
        self.assertEqual(status['trabalho']['estado'],'erro');self.assertEqual(status['indexados'],1)
        self.assertEqual(status['digest'],digest)

    def test_limite_total_rejeita_antes_de_gerar_vetores(self):
        self.material()
        with patch.object(IndiceSemantico,'_trechos',return_value=[{}]*20001):status=self.indexar()
        self.assertEqual(status['trabalho']['estado'],'erro');self.assertEqual(self.runtime.calls,0)
        self.assertIn('20.000',status['trabalho']['erro'])

    def test_reprocessar_excluir_cascata_e_retoma_incremental(self):
        cid,mid=self.material();self.indexar()
        with self.app._banco() as (h,c,b):b.salvar_extracao(mid,Extracao([(8,'Uma implicação condicional.')],'pronto',metodo='PDF textual'))
        self.assertEqual(self.op('semantica_status')['indexados'],0)
        self.indexar()
        with self.app._banco() as (h,c,b):
            self.assertFalse(recuperar_chat(b,cid,'inclinação tangente'))
            b.excluir(mid)
            for table in ('semantica_preparo','semantica_vetores','trechos'):self.assertEqual(h.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
    def test_novo_digest_exige_reindexar_sem_misturar(self):
        cid,mid=self.material();self.indexar();self.runtime.digest='novo-digest'
        report={}
        with self.app._banco() as (h,c,b):
            fs=recuperar_chat(b,cid,'derivada',report);self.assertTrue(fs);self.assertIn('Reindexe',report['aviso'])
        s=self.indexar();self.assertEqual(s['digest'],'novo-digest');self.assertEqual(s['indexados'],1)
    def test_troca_de_pesos_durante_consulta_nao_mistura_vetores(self):
        cid,mid=self.material();self.indexar();old=Embeddings.gerar
        def trocar(client,*args,**kwargs):
            result=old(client,*args,**kwargs)
            if kwargs.get('consulta'):self.runtime.digest='mudou-durante-busca'
            return result
        report={}
        with patch.object(Embeddings,'gerar',trocar), self.app._banco() as (h,c,b):
            result=recuperar_chat(b,cid,'derivada',report)
        self.assertTrue(result);self.assertEqual(report['metodo'],'busca textual')
        self.assertIn('durante a busca',report['aviso'])

    def test_runtime_offline_retorna_textual_e_avisa(self):
        cid,mid=self.material();self.indexar()
        with patch.object(Embeddings,'identidade',side_effect=RuntimeError('Servidor indisponível')):
            p=self.op('previa',id=cid,texto='derivada',modo='Explicar')
        self.assertEqual(p['fontes'][0]['material_id'],mid);self.assertIn('Usando busca textual',p['recuperacao']['aviso'])
    def test_indice_parcial_e_corrompido_nao_vira_fonte_inventada(self):
        cid,mid=self.material();self.indexar()
        with self.app._banco() as (h,c,b):
            with h.db:h.db.execute("UPDATE semantica_vetores SET vetor=x'0000'")
            report={};self.assertFalse(recuperar_chat(b,cid,'inclinação tangente',report));self.assertIn('vetores válidos',report['aviso'])
        self.indexar();self.assertEqual(self.op('semantica_status')['indexados'],1)
    def test_formato_invalido_e_remoto_nao_publicam(self):
        self.material()
        for kind in ('dimensao','nan','zero'):
            self.runtime.invalid=kind;s=self.indexar();self.assertEqual(s['trabalho']['estado'],'erro');self.assertEqual(s['indexados'],0)
        self.runtime.invalid=None;self.runtime.remote=True;s=self.indexar()
        self.assertEqual(s['trabalho']['estado'],'erro');self.assertIn('cloud',s['trabalho']['erro'])
    def test_desativar_preserva_indice_e_nunca_consulta_runtime(self):
        cid,mid=self.material();self.indexar();self.op('semantica_ativar',valor=False);self.runtime.requests.clear()
        with self.app._banco() as (h,c,b):self.assertTrue(recuperar_chat(b,cid,'derivada'))
        self.assertEqual(self.runtime.requests,[]);self.assertEqual(self.op('semantica_status')['indexados'],1)
    def test_material_mudou_durante_preparo_nao_publica(self):
        cid,mid=self.material();old=Embeddings.gerar
        def alterar(client,*a,**kw):
            vectors=old(client,*a,**kw)
            with Historico(self.path).db as db:db.execute('DELETE FROM trechos WHERE material_id=?',(mid,))
            return vectors
        with patch.object(Embeddings,'gerar',alterar):s=self.indexar()
        self.assertEqual(s['trabalho']['estado'],'erro');self.assertEqual(s['indexados'],0)
    def test_input_e_confirmacao_antes_de_mutacoes(self):
        self.material()
        for args in ({},{'confirmado':True,'url':'http://evil.example:11434'}):
            with self.assertRaises(ValueError):self.op('semantica_indexar',**args)
        self.assertIsNone(self.op('semantica_status')['trabalho']);self.assertEqual(self.runtime.calls,0)


class MigracaoSemanticaTest(unittest.TestCase):
    def test_backup_e_rollback_v7(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'h.sqlite3';h=Historico(path);cid=h.criar();h.adicionar(cid,'user','Mensagem anterior');h.fechar()
            with sqlite3.connect(path) as db:
                for table in ('semantica_config','semantica_vetores','semantica_preparo','semantica_trabalho'):db.execute('DROP TABLE '+table)
                db.execute('DROP TRIGGER semantica_texto_alterado');db.execute('DROP TABLE IF EXISTS calculos');db.execute('PRAGMA user_version=7')
            def fail(db):db.execute('CREATE TABLE lixo(id)');raise RuntimeError('falha simulada')
            with patch('tutor_calculo.semantica.migrar_semantica',fail),self.assertRaises(RuntimeError):Historico(path)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],7)
                self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='lixo'").fetchone())
            h=Historico(path)
            self.assertEqual(h.db.execute('PRAGMA user_version').fetchone()[0],10);self.assertEqual(h.mensagens(cid)[0]['texto'],'Mensagem anterior');h.fechar()
            with sqlite3.connect(str(path)+'.v7.backup') as db:self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],7)

if __name__=='__main__':unittest.main()
