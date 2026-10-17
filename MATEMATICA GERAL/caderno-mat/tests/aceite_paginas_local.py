"""Proposta L4 real em Ollama, versões separadas e exportação local."""
import json
from pathlib import Path
import sys,tempfile,time
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.paginas import nova
from tutor_calculo.piloto_local import isolamento

def wait(app,jid,limit=200):
 end=time.monotonic()+limit
 while time.monotonic()<end:
  j=app.executar('pagina_job',{'id':jid})
  if j['estado']!='executando':return j
  time.sleep(.2)
 raise RuntimeError('Aceite excedeu o limite.')
def main():
 report={'isolamento':isolamento(),'modelo':'qwen3.5:4b-q4_K_M'}
 with tempfile.TemporaryDirectory(prefix='cadernomat-l4-real-') as tmp:
  app=Aplicacao(Path(tmp)/'h.sqlite3')
  try:
   app._ia_preferencias.salvar('ollama',{'modelo':report['modelo'],'url':'http://127.0.0.1:11434','contexto':4096,'timeout':180})
   p=app.executar('pagina_criar',{'caderno':None});c=nova('Derivada de uma potência');c['secoes'][0].update(titulo='Dados para organizar',texto='Enunciado: derive f(x)=x². Resultado informado: derivada f′(x)=2x. Regra usada: potência.')
   p=app.executar('pagina_rascunho',{'id':p['id'],'conteudo':c,'revisao':p['revisao']});app.executar('pagina_salvar',{'id':p['id']});v1=app.executar('pagina_versao',{'id':p['id'],'versao':1})
   with patch('openai.OpenAI',side_effect=AssertionError('online proibido')),patch('tutor_calculo.gemini.consultar',side_effect=AssertionError('online proibido')):
    j=app.executar('pagina_previa',{'id':p['id'],'secoes':[c['secoes'][0]['id']],'materiais':[]});assert j['previa']['selecao']['provedor']=='ollama';start=time.monotonic();app.executar('pagina_consultar',{'id':j['id']});r=wait(app,j['id']);report.update(segundos=round(time.monotonic()-start,2),estado=r['estado'],erro=r['erro'])
    assert app.executar('pagina_obter',{'id':p['id']})['rascunho']==c
    report['sem_aplicacao_automatica']=True
    if r['estado']=='concluida':
     report['proposta']=r['resultado'];app.executar('pagina_aceitar',{'id':p['id'],'trabalho':j['id']});app.executar('pagina_salvar',{'id':p['id']});job=app.executar('pagina_exportar',{'id':p['id'],'versao':2});export=wait(app,job['id'],100);report.update(exportacao=export['estado'],aviso_exportacao=export['erro'],folhas=(export['manifesto'] or {}).get('folhas'))
     assert app.executar('pagina_versao',{'id':p['id'],'versao':1})==v1;report['versao_anterior_preservada']=True
  finally:app.fechar();app._executor.shutdown(wait=True)
 path=Path.home()/'.local/share/CadernoMat/ia-local/aceite-paginas.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2));path.chmod(0o600);print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
