"""Janela Qt com banco fictício; runtime simulado ou aceite local explícito."""
import os
import sys
import time
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.desktop import abrir
from tutor_calculo.servico import Aplicacao
from tutor_calculo.piloto_local import isolamento

if __name__=='__main__':
    pasta=Path(os.environ['CADERNOMAT_TEST_DIR'])
    runtime=None
    if os.environ.get('CADERNOMAT_REAL_LOCAL')!='1':
        from test_ollama import RuntimeSimulado
        runtime=RuntimeSimulado(int(os.environ['CADERNOMAT_OLLAMA_PORT']))
        runtime.hold=True
        runtime.text="### Consulta local\nO mini-simulado tem **7 questões** e **23 minutos**, segundo notas.txt [M1].\n\nA fórmula $2+2=4$ é apenas um exemplo."
    else:
        import json
        (pasta/'isolamento.json').write_text(json.dumps(isolamento()))
    app=Aplicacao(pasta/'historico.sqlite3')
    def finalizar():
        import webview
        while not (pasta/'sair').exists():time.sleep(.1)
        webview.windows[0].destroy()
    Thread(target=finalizar,daemon=True).start()
    def proibido(*args,**kwargs):raise AssertionError('O teste local tentou chamar um provedor online.')
    try:
        with patch('openai.OpenAI',side_effect=proibido),patch('tutor_calculo.gemini.consultar',side_effect=proibido), \
             patch('tutor_calculo.servico.configuracao',return_value=('','modelo-online-inativo')), \
             patch('tutor_calculo.servico.provedor_ativo',return_value='gemini'), \
             patch('tutor_calculo.estudo.configuracao',return_value=('','modelo-online-inativo')), \
             patch('tutor_calculo.estudo.provedor_ativo',return_value='gemini'), \
             patch('webview.window.Window.create_file_dialog',return_value=(str(pasta/'notas.txt'),)):
            abrir(app)
    finally:
        if runtime:runtime.close()
