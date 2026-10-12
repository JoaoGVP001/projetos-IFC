"""Reproduções de redações observadas e contraprovas dos filtros conservadores."""
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch
from tutor_calculo.revisao_respostas import conferir,escopo,RespostaRetida
from tutor_calculo.ia import perguntar,limitar_contexto
from tutor_calculo.servico import Aplicacao
from tutor_calculo.provedores.contratos import RespostaIncompleta
from test_ollama import RuntimeSimulado


class RevisaoRespostasTest(unittest.TestCase):
    def test_retem_passo_observado_sem_certificar_que_sempre_esta_errado(self):
        t='Passo Indutivo: Demonstrar que se $P(k)$ for verdadeiro para algum inteiro $k >= n_0$, então $P(k+1)$ também é verdadeiro.'
        with self.assertRaises(RespostaRetida) as e:conferir('Corrija minha prova de indução.',t,'Corrigir')
        self.assertIn('arbitrariamente',e.exception.metricas['qualidade']['aviso'])
        self.assertEqual(e.exception.metricas['qualidade']['rascunho_recusado'],t)
    def test_nao_retem_negacao_explicitamente_corretiva(self):
        for t in ('Não basta se P(k) é verdadeiro para algum inteiro k; fixe k arbitrário.',
                  'É errado afirmar que se P(k) vale para algum inteiro k a prova está feita.',
                  'Suponha P(k) para algum inteiro k, escolhido arbitrariamente.',
                  'Fixe k arbitrário >= 1. Se P(k) vale, demonstre P(k+1).'):
            self.assertEqual(conferir('Indução para n>=1',t,'Explicar')['sinais_encontrados'],0)
    def test_buraco_nao_recebe_nome_de_assintota_nem_desaparece_por_cancelamento(self):
        for t in ('O ponto x=1 é uma assíntota removível.',
                  'A simplificação remove um "buraco" na continuidade, mas não redefine a função.'):
            with self.subTest(t=t),self.assertRaises(RespostaRetida):conferir('Explique domínio e limite de f(x)=(x^2-1)/(x-1).',t,'Corrigir')
        for t in ('Não é uma assíntota removível: é um buraco.',
                  'A simplificação não remove o buraco do domínio original.'):
            conferir('Explique limite de f(x).',t,'Explicar')
    def test_sem_sinal_nao_significa_prova_ou_conta_validada(self):
        r=conferir('Explique indução.','Base n=1, depois conclua 1=2.','Explicar')
        self.assertIn('não verifica',r['aviso'].lower());self.assertNotIn('correta',str(r))
        self.assertEqual(escopo('Olá','Explicar'),[])
        self.assertEqual(escopo('indução','Gerar atividade'),[])
    def test_testemunha_inteira_m_nao_e_quantificador_sobre_k(self):
        t='Fixe k arbitrário>=1 e suponha 5^k−1=4m para algum inteiro m. Então 5^(k+1)−1=4(5m+1).'
        self.assertEqual(conferir('Prove por indução a divisibilidade.',t,'Explicar')['sinais_encontrados'],0)
    def test_http_retem_antes_de_exibir_e_sem_segunda_chamada(self):
        r=RuntimeSimulado();self.addCleanup(r.close);r.text='Se P(k) vale para algum inteiro k, então P(k+1) vale.';pieces=[];metrics={}
        with self.assertRaises(RespostaRetida):perguntar('Explique indução.',modo='Explicar',provedor='ollama',local=r.config,trecho=pieces.append,metricas=metrics.update)
        self.assertEqual(pieces,[]);self.assertEqual(metrics['qualidade']['estado'],'recusada')
        self.assertEqual(sum(path=='/api/chat' for path,_ in r.requests),1)
    def test_online_simulado_tambem_retem_sem_nova_chamada(self):
        with patch('tutor_calculo.ia.configuracao',return_value=('chave-ficticia','modelo-ficticio')),patch('tutor_calculo.gemini.consultar',return_value='É uma assíntota removível.') as gemini:
            with self.assertRaises(RespostaRetida):perguntar('Explique limite de f(x).',modo='Explicar',provedor='gemini')
        self.assertEqual(gemini.call_count,1)
    def test_preserva_parcial_interrompido_como_nao_concluido(self):
        r=RuntimeSimulado();self.addCleanup(r.close);r.reason='length';r.text='Base n=1. Hipótese:';pieces=[]
        with self.assertRaises(RespostaIncompleta):perguntar('Explique indução.',provedor='ollama',local=r.config,trecho=pieces.append)
        self.assertEqual(''.join(pieces),r.text)
    def test_recusa_persistente_e_excluida_de_contexto(self):
        with TemporaryDirectory() as d:
            r=RuntimeSimulado();self.addCleanup(r.close);r.text='Se P(k) vale para algum inteiro k, então P(k+1) vale.'
            app=Aplicacao(Path(d)/'h.sqlite3')
            try:
                cid=app.executar('chat_criar',{})['conversa']['id']
                app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','url':r.config['url'],'contexto':4096,'perfil':'rapido','escopo':'padrao'})
                tid=app.executar('enviar',{'id':cid,'texto':'Explique indução.','modo':'Explicar'})['tarefa']
                for _ in range(300):
                    s=app.executar('estado',{})
                    if not s['ocupado']:break
                    time.sleep(.01)
                m=s['mensagens'][-1];self.assertEqual(m['estado'],'erro');self.assertNotIn('algum inteiro k',m['texto'])
                self.assertEqual(limitar_contexto(s['mensagens']),[])
                app.fechar();app._executor.shutdown(wait=True);app=Aplicacao(Path(d)/'h.sqlite3')
                self.assertEqual(app.executar('estado',{})['mensagens'][-1]['metricas']['qualidade'],m['metricas']['qualidade'])
                with self.assertRaisesRegex(ValueError,'rascunho recusado'):app.executar('ia_ajuste_previa',{'id':tid,'acao':'continuar'})
            finally:app.fechar();app._executor.shutdown(wait=True)
    def test_rascunho_privado_preservado_sem_stream_e_cancelamento_nao_aceita_prova(self):
        with TemporaryDirectory() as d:
            r=RuntimeSimulado();self.addCleanup(r.close);r.hold=True;r.text='Hipótese ainda não revisada: P(k).'
            app=Aplicacao(Path(d)/'h.sqlite3')
            try:
                cid=app.executar('chat_criar',{})['conversa']['id']
                app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','url':r.config['url'],'contexto':4096,'perfil':'rapido','escopo':'padrao'})
                tid=app.executar('enviar',{'id':cid,'texto':'Explique indução.','modo':'Explicar'})['tarefa']
                pending=''
                for _ in range(300):
                    with app._banco() as (h,c,b):pending=h.db.execute('SELECT parcial FROM consultas_ia WHERE id=?',(tid,)).fetchone()[0]
                    if pending:break
                    time.sleep(.01)
                self.assertEqual(pending,r.text)
                self.assertFalse(app.executar('estado',{})['tarefas'][-1]['parcial'])
                app.executar('ia_cancelar',{'id':tid})
                for _ in range(300):
                    s=app.executar('estado',{})
                    if not s['ocupado']:break
                    time.sleep(.01)
                self.assertEqual(s['mensagens'][-1]['estado'],'cancelada')
                self.assertEqual(s['mensagens'][-1]['texto'],r.text)
                self.assertEqual(limitar_contexto(s['mensagens']),[])
            finally:app.fechar();r.release.set();app._executor.shutdown(wait=True)


if __name__=='__main__':unittest.main()
