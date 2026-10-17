"""Qt: PDF fictício de duas páginas, IA HTTP simulada e ferramentas reais."""
import os,sys,time,json
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.desktop import abrir
from test_ollama import RuntimeSimulado

def pdf(path):
 from pypdf import PdfWriter
 from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
 w=PdfWriter()
 for text in ('Aula ficticia de matematica.','Funcao quadratica f(x)=x^2-4x+3. Derivada: 2x-4. Figura nao interpretada.'):
  p=w.add_blank_page(width=595,height=842)
  font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
  p[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):w._add_object(font)})})
  s=DecodedStreamObject();s.set_data(('BT /F1 12 Tf 30 750 Td ('+text.replace('(',r'\(').replace(')',r'\)')+') Tj ET').encode('ascii'))
  p[NameObject('/Contents')]=w._add_object(s)
 w.write(path)

if __name__=='__main__':
 root=Path(os.environ['CADERNOMAT_TEST_DIR']);r=RuntimeSimulado();r.reason='stop';r.text=json.dumps({'evidencias':[{'referencia':'M1','citacao':'Derivada: 2x-4.'}], 'lacunas':['figura_nao_interpretada']})
 if (root/'resposta-invalida').exists():r.text=json.dumps({'evidencias':[{'referencia':'M1','citacao':'Derivada: 999.'}],'lacunas':[]})
 if (root/'resposta-inducao').exists():r.text='Se P(k) for verdadeiro para algum inteiro k, então P(k+1) também é verdadeiro.'
 app=Aplicacao(root/'historico.sqlite3')
 with app._banco() as (h,c,b):
  if not h.listar():
   bid=c.criar('Estudo confiável — teste');cid=h.criar(bid);c.salvar_navegacao(bid,cid)
   pdf(root/'aula-ficticia.pdf');mid,_=b.adicionar_arquivo(root/'aula-ficticia.pdf',cid);b.processar(mid);b.vincular(mid,cid,True)
 app.executar('configurar',{'provedor':'ollama','modelo':'teste:4b','url':r.config['url'],'contexto':4096,'perfil':'rapido','timeout':180,'escopo':'padrao'})
 def monitor():
  import webview
  while not app._fechado:
   if (root/'sair').exists():(root/'sair').unlink();webview.windows[0].destroy()
   time.sleep(.1)
 def forbidden(*a,**k):raise AssertionError('Provedor online acionado.')
 Thread(target=monitor,daemon=True).start()
 try:
  with patch('openai.OpenAI',side_effect=forbidden),patch('tutor_calculo.gemini.consultar',side_effect=forbidden):abrir(app)
 finally:r.close()
