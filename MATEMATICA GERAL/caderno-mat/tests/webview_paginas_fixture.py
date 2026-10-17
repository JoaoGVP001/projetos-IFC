"""Aceite Qt L4 com dados fictícios, exportação real e IA simulada."""
import os,json,sys,time
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.desktop import abrir
if __name__=='__main__':
 root=Path(os.environ['CADERNOMAT_TEST_DIR']);app=Aplicacao(root/'historico.sqlite3');(root/'pngs').mkdir(exist_ok=True)
 with app._banco() as (h,c,b):
  if not h.listar():
   bid=c.criar('Páginas — validação');cid=h.criar(bid);c.salvar_navegacao(bid,cid)
   h.adicionar(cid,'assistant','Exemplo fictício de estudo: $f(x)=x^2$.')
 def finish():
  import webview
  while not app._fechado:
   if (root/'sair').exists():
    (root/'sair').unlink();webview.windows[0].destroy()
   time.sleep(.1)
 def forbidden(*a,**k):raise AssertionError('Provedor online acionado no aceite.')
 def ia(*a,**k):
  if k.get('modo')=='Rotular blocos':
   data=json.JSONDecoder().raw_decode(k['preparada']['pergunta'].split('Blocos autorizados:\n',1)[1])[0]
   return json.dumps({'blocos':[{'bloco_id':('desconhecido' if (root/'ids-invalidos').exists() else x['bloco_id']),'rotulo':'Etapas de estudo'} for x in data]})
  if (root/'formula-invalida').exists():return json.dumps({'titulo':'Soma alterada','assunto':'','secoes':[{'id':'ia1','titulo':'Resumo','texto':'Notação alterada: $n=-2$.','recurso':None}]})
  data=json.JSONDecoder().raw_decode(k['preparada']['pergunta'].split('Dados escolhidos pelo usuário:\n',1)[1])[0]
  text='Uma proposta da IA, para revisão.\n'+'\n'.join(s['texto'] for s in data['trechos'])+'\nPrática: qual é a derivada de $x^2$?'
  return json.dumps({'titulo':'Revisão organizada','assunto':'Cálculo e Discreta','secoes':[{'id':'ia1','titulo':'Resumo','texto':text,'recurso':None}]})
 def dialog(self,dialog_type,*a,**k):
  import webview
  return [str(root/'copia.pdf' if dialog_type==webview.FileDialog.SAVE else root/'pngs')]
 original_execute=app._paginas.executar
 def page_execute(op,d):
  if op=='pagina_rascunho' and (root/'falhar-autosave').exists():raise RuntimeError('Falha simulada ao salvar.')
  return original_execute(op,d)
 app._paginas.executar=page_execute
 Thread(target=finish,daemon=True).start()
 with patch('openai.OpenAI',side_effect=forbidden),patch('tutor_calculo.gemini.consultar',side_effect=forbidden),patch('tutor_calculo.ia.perguntar',side_effect=ia),patch('tutor_calculo.ia.configuracao',return_value=('simulada','modelo')),patch('tutor_calculo.servico.configuracao',return_value=('simulada','modelo')),patch('webview.window.Window.create_file_dialog',new=dialog):abrir(app)
