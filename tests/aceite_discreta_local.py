"""Aceite com Ollama real, dados fictícios e clientes online proibidos."""
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.piloto_local import isolamento, Monitor


def aguardar(app, jid):
    limite = time.monotonic() + 200
    while time.monotonic() < limite:
        job = app.executar('discreta_obter', {'id': jid})
        if job['estado'] not in ('previa', 'executando'):
            if job['estado'] != 'concluida':
                raise RuntimeError(job['erro'])
            return job
        time.sleep(.2)
    raise RuntimeError('Consulta não terminou no limite do aceite.')


def main():
    report = {'isolamento': isolamento(), 'modelo': 'qwen3.5:4b-q4_K_M'}
    with tempfile.TemporaryDirectory(prefix='cadernomat-discreta-real-') as tmp, Monitor() as monitor:
        app = Aplicacao(Path(tmp) / 'h.sqlite3')
        try:
            app._ia_preferencias.salvar('ollama', {
                'modelo': report['modelo'], 'url': 'http://127.0.0.1:11434',
                'contexto': 4096, 'timeout': 180,
            })
            cid = app.executar('chat_criar', {})['conversa']['id']
            with patch('openai.OpenAI', side_effect=AssertionError('online proibido')), patch('tutor_calculo.gemini.consultar', side_effect=AssertionError('online proibido')):
                p = app.executar('discreta_previa', {
                    'conversa': cid, 'tipo': 'proposta',
                    'pedido': 'Verifique transitividade de R={(1,2),(2,3)} sobre A={1,2,3}. Não há universo U informado.',
                })
                assert p['previa']['selecao']['provedor'] == 'ollama'
                inicio = time.monotonic()
                app.executar('discreta_consultar', {'id': p['id']})
                proposal = aguardar(app, p['id'])
                report['proposta_segundos'] = round(time.monotonic() - inicio, 2)
                report['proposta'] = proposal['resultado']
                assert proposal['resultado']['tipo'] == 'relacoes'
                assert proposal['resultado']['A'] == '{1,2,3}'
                assert proposal['resultado']['R'] == '{(1,2),(2,3)}'
                assert not proposal['resultado']['U']
                assert not list((Path(tmp) / 'calculos').glob('*.png'))
                spec = {k: v for k, v in proposal['resultado'].items() if k != 'origens'}
                app.executar('discreta_validar', {'spec': spec})
                jid = app.executar('discreta_executar', {
                    'conversa': cid, 'spec': spec, 'proposta': p['id'],
                })['id']
                calc = aguardar(app, jid)
                prop = next(p for p in calc['resultado']['resultados']['propriedades'] if p['propriedade'] == 'transitiva')
                assert prop['vale'] is False and prop['contraexemplo'] == [1, 2, 3]
                report['calculo_confirmado'] = True
                p = app.executar('discreta_previa', {'conversa': cid, 'tipo': 'explicacao', 'origem': jid})
                inicio = time.monotonic()
                app.executar('discreta_consultar', {'id': p['id']})
                explanation = aguardar(app, p['id'])
                report['explicacao_segundos'] = round(time.monotonic() - inicio, 2)
                report['explicacao'] = explanation['resultado']['texto']
                assert app.executar('discreta_obter', {'id': jid})['resultado'] == calc['resultado']
            app.fechar()
            app._executor.shutdown(wait=True)
            app = Aplicacao(Path(tmp) / 'h.sqlite3')
            assert app.executar('discreta_obter', {'id': jid})['imagem'] == calc['imagem']
            report['reinicio_preservado'] = True
        finally:
            app.fechar()
            app._executor.shutdown(wait=True)
    report['recursos'] = monitor.samples
    target = Path.home() / '.local/share/CadernoMat/ia-local/aceite-discreta.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    target.chmod(0o600)
    print(json.dumps({k: v for k, v in report.items() if k != 'recursos'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
