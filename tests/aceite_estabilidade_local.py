"""Piloto finito 4B em CPU/GPU observado; saídas fictícias fora do Git."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.piloto_local import isolamento
from tutor_calculo.ia import preparar_consulta,perguntar
from tutor_calculo.provedores.ollama import Ollama

if __name__=='__main__':
 args=argparse.ArgumentParser();args.add_argument('--confirmacao',action='store_true');args.add_argument('--saida',type=Path);cli=args.parse_args()
 out=cli.saida or Path.home()/'.local/share/CadernoMat/ia-local/relatorios'/('estabilidade-confirmacao.json' if cli.confirmacao else 'estabilidade.json')
 out.parent.mkdir(parents=True,exist_ok=True)
 query='Consegue explicar indução matemática, dar um exemplo da soma dos naturais e mostrar uma ilustração para ajudar?'
 records=[];start=time.monotonic();network=isolamento()
 cases=[('rapido',query)] if cli.confirmacao else [('rapido',query),('estudo',query),('rapido','Explique por que testar uma fórmula para n=1,2,3 não é uma prova por indução.')]
 for profile,request in cases:
  if time.monotonic()-start>420:break
  conf={'modelo':'qwen3.5:4b-q4_K_M','contexto':4096,'timeout':180 if profile=='rapido' else 240,'perfil':profile}
  client=Ollama(conf);state=client.diagnostico()['dispositivo'];book={'nome':'Matemática Discreta · fictício','preferencia':'completa','objetivo':'Compreender demonstrações','orientacao':'Explique etapas e hipóteses.'} if cli.confirmacao else None
  prepared=preparar_consulta(request,modo='Explicar',provedor='ollama',local=conf,caderno=book)
  pieces=[];metrics={};error=''
  try:answer=perguntar(request,modo='Explicar',provedor='ollama',local=conf,preparada=prepared,trecho=pieces.append,metricas=metrics.update)
  except Exception as e:answer=''.join(pieces);error=str(e)
  records.append({'perfil':profile,'pedido':request,'estado':'erro' if error else 'concluida','erro':error,'carregamento_antes':state['estado'],'texto':answer,'metricas':metrics,'orcamento':prepared['orcamento']})
  out.write_text(json.dumps({'isolamento':network,'amostras':records},ensure_ascii=False,indent=2));out.chmod(0o600)
  print(json.dumps({'perfil':profile,'erro':error,'segundos':metrics.get('segundos'),'saida':metrics.get('tokens_saida'),'motivo':metrics.get('motivo')},ensure_ascii=False),flush=True)
