import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

from tutor_calculo.piloto_local import ClienteLocal, avaliar, esquema, esquema_atividade, expressao_curta, fontes_ficticias


class PilotoTest(unittest.TestCase):
    def test_destino_somente_loopback_sem_credenciais(self):
        for url in ['https://127.0.0.1:11434', 'http://localhost:11434', 'http://example.com:11434',
                    'http://user:secret@127.0.0.1:11434', 'http://@127.0.0.1:11434',
                    'http://:@127.0.0.1:11434', 'http://127.0.0.1:11434/x',
                    'http://127.0.0.1:11434?q=1', 'http://127.0.0.1:11434#x', 'http://127.0.0.1']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                ClienteLocal(url)

    def test_esquema_nao_entrega_gabarito_ou_forca_ausencia(self):
        schema = esquema({'quantidade': 238, 'professor': None, 'converge': False})
        text = json.dumps(schema)
        self.assertNotIn('238', text)
        self.assertNotIn('const', text)
        self.assertNotIn('enum', text)
        self.assertEqual(schema['properties']['respostas']['properties']['professor']['type'], ['string', 'null'])
        self.assertEqual(list(schema['properties']), ['explicacao', 'respostas'])

    def test_atividade_exige_metadados_textuais_e_nao_entrega_resposta(self):
        schema = esquema_atividade()
        self.assertEqual(schema['properties']['assuntos']['type'], 'string')
        self.assertEqual(schema['properties']['etiquetas']['type'], 'string')
        question = schema['properties']['exercicios']['items']['properties']
        self.assertEqual(question['resposta'], {'type': 'string'})
        self.assertLess(list(question).index('explicacao'), list(question).index('resposta'))

    def test_ausencia_nao_passa_por_falta_de_campo(self):
        self.assertFalse(avaliar('{"respostas":{}}', {'professor': None})['passou'])
        self.assertTrue(avaliar('{"respostas":{"professor":null}}', {'professor': None})['passou'])

    def test_numeros_booleanos_e_equivalencia(self):
        self.assertTrue(avaliar('{"respostas":{"derivada":"-4+2*x","integral":"1/3","vf":false}}',
                               {'derivada': '2*x-4', 'integral': '1/3', 'vf': False})['passou'])
        self.assertFalse(avaliar('{"respostas":{"n":true}}', {'n': 1})['passou'])
        self.assertFalse(avaliar('{"respostas":{"vf":0}}', {'vf': False})['passou'])

    def test_expressao_limita_codigo_e_complexidade(self):
        for text in ["__import__('os').system('echo teste')", '2**999999', '2**(2**9)', '1e100', '1+' * 50 + '1']:
            with self.subTest(text=text), self.assertRaises((ValueError, SyntaxError)):
                expressao_curta(text)

    def test_rag_usa_extracao_fts_e_exclui_material_nao_selecionado(self):
        with tempfile.TemporaryDirectory() as tmp:
            sources = fontes_ficticias(Path(tmp))
            text = json.dumps(sources, ensure_ascii=False)
            self.assertIn('23 minutos', text)
            self.assertIn('Apostila-piloto.txt', text)
            self.assertNotIn('Professor Intruso', text)
            self.assertNotIn('Outro-caderno.txt', text)

    def server(self, status, payload):
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', 0)))
                self.send_response(status)
                if status == 302:
                    self.send_header('Location', 'http://example.com')
                self.end_headers()
                for chunk in payload:
                    self.wfile.write(chunk)
                    self.wfile.flush()
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return ClienteLocal(f'http://127.0.0.1:{server.server_port}')

    def test_stream_ndjson_em_fragmentos_metricas(self):
        payload = b'{"message":{"content":"Ol"},"done":false}\n{"message":{"content":"a"},"done":true,"done_reason":"stop","eval_count":2,"eval_duration":1000000000}\n'
        cliente = self.server(200, [payload[:30], payload[30:65], payload[65:]])
        fragments = []
        answer = cliente.consultar([{'role': 'user', 'content': 'oi'}], trecho=fragments.append)
        self.assertEqual(answer['texto'], 'Ola')
        self.assertEqual(fragments, ['Ol', 'a'])
        self.assertEqual(answer['tokens_s'], 2)
        self.assertIsNotNone(answer['primeiro_token_s'])

    def test_resposta_parcial_nao_conclui(self):
        cliente = self.server(200, [b'{"message":{"content":"parcial"},"done":false}\n'])
        with self.assertRaisesRegex(RuntimeError, 'incompleta'):
            cliente.consultar([{'role': 'user', 'content': 'oi'}])

    def test_limite_nao_conclui(self):
        cliente = self.server(200, [b'{"message":{"content":"parcial"},"done":true,"done_reason":"length"}\n'])
        with self.assertRaisesRegex(RuntimeError, 'limite'):
            cliente.consultar([{'role': 'user', 'content': 'oi'}])

    def test_erro_servidor_claro(self):
        cliente = self.server(500, [b'{"error":"fake"}\n'])
        with self.assertRaisesRegex(RuntimeError, 'HTTP 500'):
            cliente.consultar([{'role': 'user', 'content': 'oi'}])

    def test_redirecionamento_bloqueado(self):
        cliente = self.server(302, [])
        with self.assertRaisesRegex(RuntimeError, 'redirecionar'):
            cliente.consultar([{'role': 'user', 'content': 'oi'}])

    def test_cloud_e_contexto_nao_aceitos(self):
        cliente = ClienteLocal()
        for modelo in ('qwen:cloud', 'qwen:CLOUD'):
            with self.subTest(modelo=modelo), self.assertRaises(ValueError):
                cliente.consultar([], modelo=modelo)
        with self.assertRaises(ValueError):
            cliente.consultar([], contexto=100000)


if __name__ == '__main__':
    unittest.main()
