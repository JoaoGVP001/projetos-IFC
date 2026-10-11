"""Qt real, banco fictício e chamadas online proibidas no aceite matemático."""
import os
import json
import sys
import time
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.desktop import abrir

if __name__=='__main__':
    root=Path(os.environ['CADERNOMAT_TEST_DIR']);app=Aplicacao(root/'historico.sqlite3')
    with app._banco() as (h,c,b):
        if not h.listar():
            bid=c.criar('Cálculo — validação L3');cid=h.criar(bid);c.salvar_navegacao(bid,cid)
    def finish():
        import webview
        while not (root/'sair').exists():time.sleep(.1)
        webview.windows[0].destroy()
    def forbidden(*args,**kwargs):raise AssertionError('Uma API online foi acionada durante o teste local.')
    def simulated(pergunta,**kwargs):
        if kwargs.get('modo')=='Propor cálculo':
            return json.dumps({'expressao':'x^2-4*x+3','inicio':'-2','fim':'6','ponto':'3','operacoes':['grafico','derivada','tangente']})
        return 'A derivada registrada é $2x-4$ e a tangente em $x=3$ é $y=2x-6$. O domínio original é real. Pergunta de prática: qual é a inclinação em $x=4$?'
    Thread(target=finish,daemon=True).start()
    with patch('openai.OpenAI',side_effect=forbidden),patch('tutor_calculo.gemini.consultar',side_effect=forbidden), \
         patch('tutor_calculo.servico.configuracao',return_value=('chave-simulada','modelo-inativo')), \
         patch('tutor_calculo.ia.configuracao',return_value=('chave-simulada','modelo-inativo')), \
         patch('tutor_calculo.ia.perguntar',side_effect=simulated), \
         patch('tutor_calculo.servico.provedor_ativo',return_value='gemini'), \
         patch('webview.window.Window.create_file_dialog',return_value=[str(root/'grafico-exportado.png')]):
        abrir(app)
