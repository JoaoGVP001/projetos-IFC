"""Aceites matemáticos e persistência L3; nenhuma chamada a provedor online."""
import base64
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Timer
import time
import unittest
from unittest.mock import patch
import sympy as sp
from tutor_calculo.matematica import expressao, X
from tutor_calculo.ferramentas_matematicas import calcular, validar_spec, parametros_do_pedido
from tutor_calculo.calculos import processo
from tutor_calculo.provedores.contratos import Cancelamento, ConsultaCancelada
from tutor_calculo.servico import Aplicacao
from tutor_calculo.armazenamento import Historico
from tutor_calculo.ponte import Ponte


def spec(f='x^2-4*x+3',inicio='-2',fim='6',ponto='3',ops=None):
    return dict(expressao=f,inicio=inicio,fim=fim,ponto=ponto,operacoes=ops or ['grafico','derivada','criticos','tangente'])


class MotorTest(unittest.TestCase):
    def test_quadratica_derivada_extremos_tangente_e_png(self):
        r=calcular(spec());d,c,t=r['resultados']
        self.assertEqual(d['valor']['texto'],'2*x - 4')
        self.assertEqual(c['minimo_absoluto']['x']['texto'],'2');self.assertEqual(c['minimo_absoluto']['y']['texto'],'-1')
        self.assertEqual(t['reta']['texto'],'2*x - 6')
        self.assertTrue(base64.b64decode(r['png']).startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertEqual(len(r['segmentos']),1)
        self.assertEqual([p['x']['texto'] for p in c['maximos_intervalo']],['-2','6'])

    def test_polos_tan_e_buraco_original(self):
        for f,holes in [('1/x',[0]),('(x^2-1)/(x-1)',[1]),('tan(x)',[-float(sp.pi)/2,float(sp.pi)/2])]:
            with self.subTest(f=f):
                r=calcular(spec(f,'-4','4','', ['grafico']))
                self.assertEqual(len(r['segmentos']),len(holes)+1)
                for s in r['segmentos']:
                    for p in holes:self.assertFalse(min(s['x'])<=p<=max(s['x']))

    def test_raizes_logs_valores_fora_e_cuspides(self):
        for f,limite in [('sqrt(x)',0),('log(x)',0)]:
            r=calcular(spec(f,'-4','4','-1',['valor']))
            self.assertTrue(all(x>=limite for s in r['segmentos'] for x in s['x']))
            self.assertEqual(r['resultados'][0]['estado'],'nao_verificado')
        for f in ['abs(x)','sqrt(x^2)','sqrt(x)','0*sqrt(x)']:
            with self.subTest(f=f):
                r=calcular(spec(f,'-4','4','0',['tangente']))
                self.assertEqual(r['resultados'][0]['estado'],'nao_verificado')
        self.assertEqual(expressao('sqrt(x^2)'),sp.Abs(X))
        r=calcular(spec('(x^2-1)/(x-1)','-4','4','1',['valor','tangente']))
        self.assertTrue(all(x['estado']=='nao_verificado' for x in r['resultados']))

    def test_integral_area_diferencas_e_recusa_impropria(self):
        r=calcular(spec('x^2','0','1','',['integral']))
        self.assertEqual(r['resultados'][0]['valor']['texto'],'1/3')
        r=calcular(spec('x','-1','1','',['integral','area']))
        self.assertEqual([q['valor']['texto'] for q in r['resultados']],['0','1'])
        for f in ['1/x','1/x^2','(x^2-1)/(x-1)']:
            r=calcular(spec(f,'-2','2','',['integral']))
            self.assertEqual(r['resultados'][0]['estado'],'nao_verificado')

    def test_extremos_intervalo_e_global_restrito(self):
        r=calcular(spec('x^2','1','2','',['criticos']))['resultados'][0]
        self.assertEqual(r['minimo_intervalo']['x']['texto'],'1')
        self.assertEqual(r['minimo_absoluto']['x']['texto'],'0')
        r=calcular(spec('x^2*(x-10)/(x-10)','1','2','',['criticos']))['resultados'][0]
        self.assertNotIn('minimo_absoluto',r)
        r=calcular(spec('x^5','1','2','',['criticos']))['resultados'][0]
        self.assertEqual(r['estado'],'nao_verificado')

    def test_parser_rejeita_codigo_e_crescimento(self):
        for f in ["__import__('os').system('touch /tmp/pwned')",'x.__class__','[x for x in (1,)]','lambda x:x','x[0]','sin(x,1)','1e309','x^x','x^100','(x^12)^12','sqrt(-1)^2','((((1000000^12)^12)^12)^12)', '(' * 20+'x'+')'*20, '+'.join(['x']*70), 'unknown(x)']:
            # Parênteses redundantes não aumentam o AST; substituir pelo caso profundo real.
            if f.startswith('('*20):f='sin('*20+'x'+')'*20
            with self.subTest(f=f),self.assertRaises(ValueError):expressao(f)
        self.assertEqual(expressao('0.1+0.2'),sp.Rational(3,10))
        for s in [spec(inicio='1',fim='1'),spec(inicio='-10001'),spec('x',ops=['shell'])]:
            with self.assertRaises(ValueError):calcular(s)

    def test_parametros_explicitamente_copiados_sem_inventar(self):
        r=parametros_do_pedido(spec(), 'Quero um gráfico de uma parábola.')
        self.assertEqual([r[k] for k in ('expressao','inicio','fim','ponto')],['','','',''])
        r=parametros_do_pedido(spec(),'f(x)=x²-4x+3; intervalo [-2,6]; tangente em x=1e3')
        self.assertEqual(r['expressao'],'x^2-4*x+3');self.assertEqual(r['ponto'],'1e3')
        r=parametros_do_pedido(spec(),'f(x)=x^2; intervalo [0,1] ou [2,3]; x=2 ou x=3')
        self.assertEqual(r['inicio'],'');self.assertEqual(r['fim'],'');self.assertEqual(r['ponto'],'')

    def test_timeout_e_cancelamento_encerram_worker(self):
        with self.assertRaisesRegex(RuntimeError,'excedeu'):processo(spec(),Cancelamento(),timeout=.00001)
        token=Cancelamento();timer=Timer(.02,token.cancelar);timer.start()
        try:
            with self.assertRaises(ConsultaCancelada):processo(spec(),token)
        finally:timer.join()


class PersistenciaTest(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.path=Path(self.tmp.name)/'historico.sqlite3'
        self.app=Aplicacao(self.path);self.cid=self.app.executar('chat_criar',{})['conversa']['id']
    def tearDown(self):self.app.fechar();self.app._executor.shutdown(wait=True);self.tmp.cleanup()
    def esperar(self,jid):
        end=time.monotonic()+30
        while time.monotonic()<end:
            r=self.app.executar('math_obter',{'id':jid})
            if r['estado']!='executando':return r
            time.sleep(.03)
        self.fail('worker não concluiu')
    def test_fluxo_offline_reinicio_e_artefato_por_id(self):
        with patch('openai.OpenAI',side_effect=AssertionError('online')),patch('tutor_calculo.gemini.consultar',side_effect=AssertionError('online')):
            jid=self.app.executar('math_executar',{'conversa':self.cid,'spec':spec()})['id'];r=self.esperar(jid)
        self.assertEqual(r['estado'],'concluida');self.assertTrue(r['imagem'])
        self.assertNotIn('artefato',r);self.assertNotIn('hash',r)
        before=self.app.executar('estado',{})['mensagens']
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        self.assertEqual(self.app.executar('estado',{})['mensagens'],before)
        self.assertEqual(self.app.executar('math_obter',{'id':jid})['imagem'],r['imagem'])
        with self.assertRaises(ValueError):self.app._calculos.png('../../etc/passwd')
        file=next((self.path.parent/'calculos').glob('*.png'));file.write_bytes(b'alterado')
        self.assertIn('alterado',self.app.executar('math_obter',{'id':jid})['aviso_artefato'])

    def test_cancelamento_sem_publicacao_e_recuperacao(self):
        jid=self.app.executar('math_executar',{'conversa':self.cid,'spec':spec()})['id']
        self.app.executar('math_cancelar',{'id':jid});r=self.esperar(jid)
        self.assertEqual(r['estado'],'cancelada');self.assertIsNone(r['resultado']);self.assertEqual(list((self.path.parent/'calculos').glob('*.png')),[])
        with self.app._banco() as (h,c,b):
            with h.db:h.db.execute("UPDATE calculos SET estado='executando' WHERE id=?",(jid,))
        self.app.fechar();self.app._executor.shutdown(wait=True);self.app=Aplicacao(self.path)
        self.assertEqual(self.app.executar('math_obter',{'id':jid})['estado'],'interrompida')
        self.assertFalse(self.app.executar('estado',{})['ocupado'])

    def test_migracao_v8_backup_preserva_e_rollback(self):
        self.app.fechar();self.app._executor.shutdown(wait=True)
        with sqlite3.connect(self.path) as db:
            db.execute('DROP TABLE calculos');db.execute('PRAGMA user_version=8')
            old=db.execute('SELECT * FROM conversas').fetchall()
        def falhar(db):db.execute('CREATE TABLE falha(v)');raise RuntimeError('falha')
        with patch('tutor_calculo.calculos.migrar_calculos',side_effect=falhar),self.assertRaises(RuntimeError):Historico(self.path)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],8)
            self.assertFalse(db.execute("SELECT name FROM sqlite_master WHERE name='falha'").fetchone())
        self.app=Aplicacao(self.path)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],9)
            self.assertEqual(db.execute('SELECT * FROM conversas').fetchall(),old)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
        with sqlite3.connect(str(self.path)+'.v8.backup') as db:self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],8)

    def test_primeira_execucao_cria_pastas_fora_do_git(self):
        path=self.path.parent/'nova-pasta'/'subpasta'/'historico.sqlite3'
        other=Aplicacao(path)
        try:
            self.assertTrue(path.is_file());self.assertTrue((path.parent/'calculos').is_dir())
        finally:other.fechar();other._executor.shutdown(wait=True)

    def test_exportacao_seletor_nativo(self):
        jid=self.app.executar('math_executar',{'conversa':self.cid,'spec':spec()})['id'];self.esperar(jid)
        from unittest.mock import Mock
        p=Ponte(self.app);p._window=Mock();out=self.path.parent/'exportado.png';p._window.create_file_dialog.return_value=[str(out)]
        self.assertTrue(p.request('math_exportar',{'id':jid})['ok'])
        self.assertEqual(out.read_bytes(),self.app._calculos.png(jid))
        p._window.create_file_dialog.return_value=None
        self.assertFalse(p.request('math_exportar',{'id':jid})['data']['exportado'])


class PropostasTest(unittest.TestCase):
    tearDown=PersistenciaTest.tearDown
    esperar=PersistenciaTest.esperar
    def setUp(self):
        PersistenciaTest.setUp(self)
        self.app._ia_preferencias.salvar('ollama',{'modelo':'teste:4b','url':'http://127.0.0.1:11434','contexto':4096,'timeout':180})
    def previa(self,tipo='proposta',**extra):
        return self.app.executar('math_previa',{'conversa':self.cid,'tipo':tipo,'pedido':'Trace f(x)=x^2-4*x+3 no intervalo [-2,6] e a tangente em x=3.',**extra})
    def consultar(self,p,output):
        with patch('tutor_calculo.ia.perguntar',return_value=output) as mock,patch('tutor_calculo.ia.configuracao',return_value=('simulada','modelo')):
            self.app.executar('math_consultar',{'id':p['id']});r=self.esperar(p['id'])
            return r,mock.call_args
    def test_proposta_revisavel_sem_executar_e_parametros_ausentes(self):
        p=self.previa();self.assertEqual(p['estado'],'previa');self.assertEqual(p['previa']['fontes'],[])
        self.assertEqual(p['previa']['historico'],[]);self.assertFalse(p['previa']['originais_enviados'])
        r,call=self.consultar(p,json.dumps(spec()))
        self.assertEqual(r['estado'],'concluida');self.assertEqual(r['resultado']['expressao'],spec()['expressao'])
        self.assertEqual(call.kwargs['provedor'],'ollama');self.assertIsNotNone(call.kwargs['formato'])
        self.assertEqual(list((self.path.parent/'calculos').glob('*.png')),[])
        p=self.previa(pedido='Faça um gráfico.');r,_=self.consultar(p,json.dumps(spec()))
        self.assertEqual(r['resultado']['inicio'],'');self.assertEqual(r['resultado']['fim'],'')
        with self.assertRaises(ValueError):self.app.executar('math_executar',{'conversa':self.cid,'spec':r['resultado']})
    def test_json_e_codigo_rejeitados_sem_artefato(self):
        for output in ['não JSON',json.dumps({**spec(),'operacoes':['shell']}),json.dumps({**spec(),'expressao':"__import__('os').system('echo oi')"}),json.dumps({**spec(),'campo_oculto':'exec'})]:
            with self.subTest(output=output):
                r,_=self.consultar(self.previa(),output);self.assertEqual(r['estado'],'erro');self.assertIsNone(r['resultado'])
        self.assertEqual(list((self.path.parent/'calculos').glob('*.png')),[])
    def test_troca_de_provedor_exige_nova_previa(self):
        p=self.previa();self.app._ia_preferencias.salvar('gemini')
        with self.assertRaisesRegex(ValueError,'mudou'):self.app.executar('math_consultar',{'id':p['id']})
    def test_tres_provedores_mesmo_contrato_sem_tool_nativa(self):
        for provider in ['ollama','gemini','openai']:
            self.app._ia_preferencias.salvar(provider)
            p=self.previa();r,call=self.consultar(p,json.dumps(spec()))
            self.assertEqual(r['estado'],'concluida');self.assertEqual(call.kwargs['provedor'],provider)
            if provider!='ollama':self.assertIsNone(call.kwargs['formato'])
    def test_explicacao_nao_altera_calculo_e_recusa_outro_chat(self):
        jid=self.app.executar('math_executar',{'conversa':self.cid,'spec':spec()})['id'];original=self.esperar(jid)
        p=self.previa('explicacao',origem=jid);self.assertNotIn('segmentos',p['previa']['preparada']['pergunta']);self.assertNotIn('base64',p['previa']['preparada']['pergunta'])
        r,_=self.consultar(p,'A derivada é 999 (resposta errada simulada).')
        self.assertEqual(r['estado'],'concluida');self.assertIn('Explicação de IA',r['resultado']['verificacao'])
        self.assertEqual(self.app.executar('math_obter',{'id':jid})['resultado'],original['resultado'])
        other=self.app.executar('chat_criar',{})['conversa']['id']
        with self.assertRaises(ValueError):self.app.executar('math_previa',{'tipo':'explicacao','origem':jid,'conversa':other})

if __name__=='__main__':unittest.main()
