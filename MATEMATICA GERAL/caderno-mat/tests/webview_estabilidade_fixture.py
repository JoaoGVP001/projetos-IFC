"""Janela real com dados fictícios e Ollama HTTP simulado, sem clientes pagos."""
import os,sys,time
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.desktop import abrir
from tutor_calculo.servico import Aplicacao
from test_ollama import RuntimeSimulado
if __name__=='__main__':
 root=Path(os.environ['CADERNOMAT_TEST_DIR']);r=RuntimeSimulado();r.reason='length';r.text='Caso base: $P(0)$.\n\n```mermaid\nA-->B'
 app=Aplicacao(root/'historico.sqlite3')
 if not app.executar('estado',{})['conversa']:app.executar('chat_criar',{})
 app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','url':r.config['url'],'contexto':4096,'timeout':180,'perfil':'rapido','escopo':'padrao'})
 def monitor():
  import webview
  while not app._fechado:
   if (root/'concluir').exists():r.reason='stop';r.text='Para todo k ≥ 0, suponha P(k) e prove P(k+1). Conclusão: vale para todo n ≥ 0.'
   if (root/'sair').exists():(root/'sair').unlink();webview.windows[0].destroy()
   time.sleep(.1)
 def forbidden(*a,**k):raise AssertionError('Cliente pago acionado.')
 Thread(target=monitor,daemon=True).start()
 try:
  with patch('openai.OpenAI',side_effect=forbidden),patch('tutor_calculo.gemini.consultar',side_effect=forbidden):abrir(app)
 finally:r.close()
