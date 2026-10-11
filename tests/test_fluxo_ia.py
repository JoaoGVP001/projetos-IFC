import os
import tempfile
import unittest
from pathlib import Path
from queue import Queue
from unittest.mock import Mock, patch

import httpx2 as httpx
import openai

from tutor_calculo.app import EXEMPLO, resolver
try:
    from tutor_calculo.desktop_legado import TutorDesktop
except ImportError:
    TutorDesktop = None
from tutor_calculo.ia import configuracao, perguntar, salvar_configuracao


class FluxoIaTest(unittest.TestCase):
    def setUp(self):
        provedor = patch('tutor_calculo.ia.provedor_ativo', return_value='openai')
        provedor.start()
        self.addCleanup(provedor.stop)

    def test_modos_e_parametros_da_consulta(self):
        for modo in ('Resolver', 'Explicar', 'Corrigir'):
            with self.subTest(modo=modo), patch('tutor_calculo.ia.configuracao', return_value=('teste', 'modelo-teste')), patch('openai.OpenAI') as cls:
                api = cls.return_value.__enter__.return_value
                api.responses.create.return_value = Mock(output_text='Resposta', status='completed')
                self.assertEqual(perguntar('Enunciado', modo), 'Resposta')
                args = api.responses.create.call_args.kwargs
                self.assertFalse(args['store'])
                self.assertEqual(args['max_output_tokens'], 4096)
                self.assertEqual(args['input'], 'Enunciado')
                self.assertIn('Tarefa desta consulta:', args['instructions'])
                cls.assert_called_once_with(api_key='teste', timeout=60.0, max_retries=0)

    def test_erros_da_api_nao_expoem_mensagem_bruta(self):
        request = httpx.Request('POST', 'https://api.openai.com/v1/responses')
        casos = [
            (openai.AuthenticationError, 401, 'recusou a chave'),
            (openai.PermissionDeniedError, 403, 'permissao'),
            (openai.NotFoundError, 404, 'Modelo indisponivel'),
            (openai.RateLimitError, 429, 'creditos'),
            (openai.InternalServerError, 500, 'HTTP 500'),
        ]
        for tipo, status, mensagem in casos:
            erro = tipo('SEGREDO-NAO-EXIBIR', response=httpx.Response(status, request=request), body=None)
            with self.subTest(status=status), patch('tutor_calculo.ia.configuracao', return_value=('teste', 'modelo')), patch('openai.OpenAI') as cls:
                cls.return_value.__enter__.return_value.responses.create.side_effect = erro
                with self.assertRaisesRegex(RuntimeError, mensagem) as capturado:
                    perguntar('Exercicio')
                self.assertNotIn('SEGREDO', str(capturado.exception))

    def test_timeout_e_conexao(self):
        request = httpx.Request('POST', 'https://api.openai.com/v1/responses')
        for erro, mensagem in [(openai.APITimeoutError(request=request), '60 segundos'), (openai.APIConnectionError(request=request), 'internet')]:
            with patch('tutor_calculo.ia.configuracao', return_value=('teste', 'modelo')), patch('openai.OpenAI') as cls:
                cls.return_value.__enter__.return_value.responses.create.side_effect = erro
                with self.assertRaisesRegex(RuntimeError, mensagem):
                    perguntar('Exercicio')

    def test_resposta_interrompida_identificada(self):
        with patch('tutor_calculo.ia.configuracao', return_value=('teste', 'modelo')), patch('openai.OpenAI') as cls:
            cls.return_value.__enter__.return_value.responses.create.return_value = Mock(output_text='Parte', status='incomplete')
            self.assertIn('Resposta interrompida', perguntar('Exercicio'))

    def test_configuracao_salva_e_recarregada_sem_reiniciar(self):
        with tempfile.TemporaryDirectory() as pasta, patch('tutor_calculo.ia.ARQUIVO_ENV', Path(pasta)/'.env'), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(configuracao()[0], '')
            salvar_configuracao('primeira', 'modelo-a')
            self.assertEqual(configuracao(), ('primeira', 'modelo-a'))
            salvar_configuracao('segunda', 'modelo-b')
            self.assertEqual(configuracao(), ('segunda', 'modelo-b'))
            with patch.dict(os.environ, {'OPENAI_API_KEY':'ambiente'}):
                self.assertEqual(configuracao()[0], 'ambiente')

    def test_resolver_com_ia_usa_api_mesmo_para_exemplo_local(self):
        with patch('tutor_calculo.app.perguntar', return_value='Interpretacao') as api:
            self.assertEqual(resolver(EXEMPLO, usar_ia=True), 'Interpretacao')
            api.assert_called_once_with(EXEMPLO, modo='Resolver')

    def test_espacos_nao_encaminham_exemplo_local_a_api(self):
        with patch('tutor_calculo.app.perguntar') as api:
            self.assertIn('nao e continua', resolver(EXEMPLO.replace('f(x)', 'f ( x )').replace('se x', 'se  x')))
            api.assert_not_called()

    @unittest.skipIf(TutorDesktop is None, "Tkinter nao disponivel neste ambiente")
    def test_falha_inesperada_libera_interface(self):
        janela = Mock()
        janela._fila = Queue()
        janela._fila_materiais = Queue()
        janela._ocupado = True
        with patch('tutor_calculo.desktop_legado.resolver', side_effect=ZeroDivisionError('falha')):
            TutorDesktop._executar(janela, 'Resolver', 'enunciado')
        TutorDesktop._verificar_fila(janela)
        self.assertFalse(janela._ocupado)
        janela.botao_enviar.configure.assert_called_with(state='normal')
        self.assertIn('falha inesperada', janela.historico.adicionar.call_args.args[2])
        janela._mostrar_conversa.assert_called_once()


if __name__ == '__main__':
    unittest.main()
