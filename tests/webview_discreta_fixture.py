"""Janela real com dados fictícios e provedores simulados, sem chaves/custos."""
import os,json,sys,time
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
            bid=c.criar('Discreta — validação');cid=h.criar(bid);c.salvar_navegacao(bid,cid)
    def finish():
        import webview
        while not (root/'sair').exists():time.sleep(.1)
        webview.windows[0].destroy()
    def forbidden(*a,**k):raise AssertionError('Provedor online acionado pelo teste.')
    def simular(pergunta,**kwargs):
        if kwargs.get('modo')=='Propor Discreta':return json.dumps({'tipo':'relacoes','sobre':True,'A':'{99}','B':None,'U':None,'R':'{(99,99)}','S':None,'C':None,'expressao':None,'comparar':None})
        return 'A transitividade falha porque (1,2) e (2,3) estão presentes e (1,3) está ausente. Confira os pares declarados. Prática: qual par você acrescentaria?'
    Thread(target=finish,daemon=True).start()
    with patch('openai.OpenAI',side_effect=forbidden),patch('tutor_calculo.gemini.consultar',side_effect=forbidden),patch('tutor_calculo.ia.perguntar',side_effect=simular),patch('tutor_calculo.servico.configuracao',return_value=('simulada','modelo')),patch('tutor_calculo.ia.configuracao',return_value=('simulada','modelo')),patch('tutor_calculo.servico.provedor_ativo',return_value='gemini'),patch('webview.window.Window.create_file_dialog',return_value=[str(root/'diagrama-exportado.png')]):abrir(app)
