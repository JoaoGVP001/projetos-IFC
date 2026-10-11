"""Janela real com banco temporario e IA simulada para Playwright/CDP.

Executada apenas pelo teste; nao modifica .env nem os dados do usuario.
"""
import os
import sys
import time
from threading import Thread
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.desktop import abrir
from tutor_calculo.servico import Aplicacao

def consultar(pergunta,**kwargs):
    time.sleep(.4)
    if 'FALHA_SIMULADA' in pergunta:raise RuntimeError('Falha simulada de conexao. Tente novamente.')
    citacao='\n\nFonte: **notas.txt** [M1].' if kwargs.get('fontes') else ''
    return r'''### Vamos construir a ideia

Para $f(x)=x^2-4x+3$, a derivada indica como a função varia.

\[f'(x)=2x-4\]

| Intervalo | Comportamento |
| --- | --- |
| $x<2$ | Decrescente |
| $x>2$ | Crescente |

O mínimo é **(2, −1)** e a tangente em $x=3$ é $y=2x-6$.

> Confira sempre o domínio e as hipóteses.

### Sua vez
Qual é o sinal da derivada em $x=4$?'''+citacao

if __name__=='__main__':
    pasta=Path(os.environ['CADERNOMAT_TEST_DIR'])
    app=Aplicacao(pasta/'historico.sqlite3')
    def fechar_pelo_teste():
        import webview
        while not (pasta/'sair').exists():time.sleep(.1)
        webview.windows[0].destroy()
    Thread(target=fechar_pelo_teste,daemon=True).start()
    with patch('tutor_calculo.servico.configuracao',return_value=('chave-simulada','modelo-simulado')), \
         patch('tutor_calculo.servico.provedor_ativo',return_value='gemini'), \
         patch('tutor_calculo.servico.perguntar',side_effect=consultar), \
         patch('webview.window.Window.create_file_dialog',return_value=(str(pasta/'notas.txt'),)):
        abrir(app)
