import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from tutor_calculo.gemini import consultar
from tutor_calculo.ia import configuracao, perguntar, provedor_ativo, salvar_configuracao


def resposta(texto='Explicacao', fim='STOP'):
    return io.BytesIO(json.dumps({'candidates':[{'content':{'parts':[{'text':'interno','thought':True},{'text':texto}]},'finishReason':fim}]}).encode())


class GeminiTest(unittest.TestCase):
    def test_envio_e_resposta(self):
        with patch('tutor_calculo.gemini.urlopen', return_value=resposta()) as abrir:
            self.assertEqual(consultar('chave-teste', 'gemini-3.8-flash', 'derive x^2', 'instrucao'), 'Explicacao')
            req = abrir.call_args.args[0]
            self.assertNotIn('chave-teste', req.full_url)
            self.assertEqual(req.get_header('X-goog-api-key'), 'chave-teste')
            dados = json.loads(req.data)
            self.assertEqual(dados['contents'][0]['parts'][0]['text'], 'derive x^2')
            self.assertEqual(dados['systemInstruction']['parts'][0]['text'], 'instrucao')
            self.assertEqual(abrir.call_args.kwargs['timeout'], 60)

    def test_modos_gemini_nao_usam_openai(self):
        for modo in ('Resolver','Explicar','Corrigir'):
            with patch('tutor_calculo.ia.provedor_ativo', return_value='gemini'), patch('tutor_calculo.ia.configuracao', return_value=('gemini-teste','gemini-3.8-flash')), patch('tutor_calculo.gemini.consultar', return_value='OK') as api, patch('openai.OpenAI') as outra:
                self.assertEqual(perguntar('Exercicio', modo), 'OK')
                self.assertIn('Tarefa desta consulta:', api.call_args.args[3])
                outra.assert_not_called()

    def test_erros_http_sem_expor_segredo(self):
        for codigo in [400,401,403,404,429,500]:
            erro = HTTPError('https://example.com', codigo, 'SEGREDO', {}, None)
            with self.subTest(codigo=codigo), patch('tutor_calculo.gemini.urlopen', side_effect=erro):
                with self.assertRaises(RuntimeError) as exc:
                    consultar('teste','gemini-3.8-flash','Exercicio','Instrucao')
                self.assertNotIn('SEGREDO',str(exc.exception))

    def test_timeout_e_conexao(self):
        for erro in [TimeoutError(),URLError('segredo')]:
            with patch('tutor_calculo.gemini.urlopen', side_effect=erro):
                with self.assertRaises(RuntimeError):
                    consultar('teste','gemini-3.8-flash','Exercicio','Instrucao')

    def test_resposta_vazia_e_bloqueada(self):
        casos = [{}, {'promptFeedback':{'blockReason':'SAFETY'}}, {'candidates':[{'finishReason':'SAFETY'}]}]
        for dados in casos:
            with patch('tutor_calculo.gemini.urlopen', return_value=io.BytesIO(json.dumps(dados).encode())):
                with self.assertRaises(RuntimeError):
                    consultar('teste','gemini-3.8-flash','Exercicio','Instrucao')

    def test_resposta_incompleta(self):
        with patch('tutor_calculo.gemini.urlopen', return_value=resposta(fim='MAX_TOKENS')):
            self.assertIn('Resposta interrompida',consultar('teste','gemini-3.8-flash','Exercicio','Instrucao'))

    def test_modelo_invalido_nao_envia_chave(self):
        with patch('tutor_calculo.gemini.urlopen') as api:
            with self.assertRaises(ValueError):
                consultar('teste','../../outro','Exercicio','Instrucao')
            api.assert_not_called()

    def test_chaves_separadas_e_troca_preserva_configuracao(self):
        with tempfile.TemporaryDirectory() as pasta, patch('tutor_calculo.ia.ARQUIVO_ENV',Path(pasta)/'.env'), patch.dict(os.environ, {}, clear=True):
            salvar_configuracao('openai-teste','modelo-openai','openai')
            salvar_configuracao('gemini-teste','gemini-3.8-flash','gemini')
            self.assertEqual(provedor_ativo(),'gemini')
            self.assertEqual(configuracao(),('gemini-teste','gemini-3.8-flash'))
            self.assertEqual(configuracao('openai'),('openai-teste','modelo-openai'))
            salvar_configuracao('','modelo-openai','openai')
            self.assertEqual(configuracao(),('openai-teste','modelo-openai'))
            self.assertEqual(configuracao('gemini')[0],'gemini-teste')

    def test_variavel_de_ambiente_tem_prioridade(self):
        with patch('tutor_calculo.ia.dotenv_values', return_value={'AI_PROVIDER':'openai','GEMINI_API_KEY':'arquivo'}), patch.dict(os.environ, {'AI_PROVIDER':'gemini','GEMINI_API_KEY':'ambiente'}, clear=True):
            self.assertEqual(provedor_ativo(),'gemini')
            self.assertEqual(configuracao()[0],'ambiente')

    def test_sem_chave_nao_faz_consulta(self):
        with patch('tutor_calculo.ia.provedor_ativo',return_value='gemini'), patch('tutor_calculo.ia.configuracao',return_value=('','gemini-3.8-flash')), patch('tutor_calculo.gemini.consultar') as api:
            with self.assertRaisesRegex(RuntimeError,'GEMINI_API_KEY'):
                perguntar('Exercicio')
            api.assert_not_called()
