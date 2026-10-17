"""Aceite real L3 com Ollama, artefatos temporários e isolamento de rede opcional."""
import json
from pathlib import Path
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.piloto_local import isolamento, Monitor


def wait(app,jid):
    until=time.monotonic()+220
    while time.monotonic()<until:
        j=app.executar('math_obter',{'id':jid})
        if j['estado'] not in ('previa','executando'):
            if j['estado']!='concluida':raise RuntimeError(j['erro'])
            return j
        time.sleep(.2)
    raise RuntimeError('Consulta não terminou no limite do aceite.')


def main():
    report={"isolamento":isolamento(),"modelo":"qwen3.5:4b-q4_K_M"}
    with tempfile.TemporaryDirectory(prefix='cadernomat-l3-real-') as tmp, Monitor() as monitor:
        app=Aplicacao(Path(tmp)/'h.sqlite3')
        try:
            app._ia_preferencias.salvar('ollama',{'modelo':report['modelo'],'url':'http://127.0.0.1:11434','contexto':4096,'timeout':180})
            cid=app.executar('chat_criar',{})['conversa']['id']
            from unittest.mock import patch
            with patch('openai.OpenAI',side_effect=AssertionError('online proibido')),patch('tutor_calculo.gemini.consultar',side_effect=AssertionError('online proibido')):
                p=app.executar('math_previa',{'conversa':cid,'tipo':'proposta','pedido':'Trace f(x)=x^2-4*x+3 no intervalo [-2,6], calcule a derivada e a tangente em x=3.'})
                started=time.monotonic();app.executar('math_consultar',{'id':p['id']});proposal=wait(app,p['id'])
                report['proposta_segundos']=round(time.monotonic()-started,2);report['proposta']=proposal['resultado']
                assert proposal['resultado']['inicio']=='-2' and proposal['resultado']['fim']=='6' and proposal['resultado']['ponto']=='3'
                assert not list((Path(tmp)/'calculos').glob('*.png'))
                spec=proposal['resultado'];spec['operacoes']=['grafico','derivada','criticos','tangente']
                jid=app.executar('math_executar',{'conversa':cid,'spec':spec})['id'];calc=wait(app,jid)
                assert calc['resultado']['resultados'][0]['valor']['texto']=='2*x - 4'
                assert calc['resultado']['resultados'][2]['reta']['texto']=='2*x - 6'
                report['calculo_confirmado']=True
                p=app.executar('math_previa',{'conversa':cid,'tipo':'explicacao','origem':jid})
                started=time.monotonic();app.executar('math_consultar',{'id':p['id']});explanation=wait(app,p['id'])
                report['explicacao_segundos']=round(time.monotonic()-started,2);report['explicacao']=explanation['resultado']['texto']
                assert app.executar('math_obter',{'id':jid})['resultado']==calc['resultado']
                ambiguous=app.executar('math_previa',{'conversa':cid,'tipo':'proposta','pedido':'Quero um gráfico de uma parábola.'})
                app.executar('math_consultar',{'id':ambiguous['id']});draft=wait(app,ambiguous['id'])
                assert not draft['resultado']['expressao'] and not draft['resultado']['inicio'] and not draft['resultado']['fim']
                report['ambiguo_sem_parametros_inventados']=True
            app.fechar();app._executor.shutdown(wait=True);app=Aplicacao(Path(tmp)/'h.sqlite3')
            assert app.executar('math_obter',{'id':jid})['imagem']==calc['imagem'];report['reinicio_preservado']=True
        finally:app.fechar();app._executor.shutdown(wait=True)
    report['recursos']=monitor.samples
    target=Path.home()/'.local/share/CadernoMat/ia-local/aceite-matematica.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2));target.chmod(0o600)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
