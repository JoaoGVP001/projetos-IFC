"""Aceite real PDF/PNG com fixtures e artefatos fora do Git."""
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.servico import Aplicacao
from tutor_calculo.paginas import nova
from pypdf import PdfReader

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/cadernomat-l4-aceite')

def esperar(app,op,jid):
    limit=time.monotonic()+100
    while time.monotonic()<limit:
        j=app.executar(op,{'id':jid})
        if j['estado']!='executando':return j
        time.sleep(.05)
    raise RuntimeError('Aceite excedeu o limite.')

def main():
    ROOT.mkdir(parents=True,exist_ok=True);app=Aplicacao(ROOT/'h.sqlite3');report=[]
    try:
        cid=app.executar('chat_criar',{})['conversa']['id']
        cases={
         'curta':('Página curta com acentos',r'A derivada de $x^2$ é $2x$. Temos $\forall x\in\mathbb{R}$.'),
         'longa':('Resolução de várias folhas','\n\n'.join('Etapa '+str(i)+r': Para $f(x)=x^2-4x+3$, a derivada é $f\prime(x)=2x-4$. Confira o sinal, as hipóteses e o domínio. Esta explicação é texto de estudo, sem certificação global.' for i in range(65))),
         'alinhada':('Equação em etapas',r'$$\begin{aligned}f(x)&=x^2-4x+3\\f\prime(x)&=2x-4\\f\prime(2)&=0\end{aligned}$$'),
         'invalida':('Fórmula inválida',r'$\comandoinexistente{x}$'),
         'larga':('Fórmula larga', r'$$\begin{matrix}'+ '&'.join(r'\frac{x^{12345}+x}{y^{67890}+y}' for _ in range(20))+r'\end{matrix}$$'),
        }
        for name,(title,text) in cases.items():
            p=app.executar('pagina_criar',{'caderno':None});content=nova(title);content['fundo']='pautado' if name=='longa' else 'branco';content['secoes'][0].update(titulo='Resolução',texto=text)
            p=app.executar('pagina_rascunho',{'id':p['id'],'conteudo':content,'revisao':p['revisao']});app.executar('pagina_salvar',{'id':p['id']});job=app.executar('pagina_exportar',{'id':p['id'],'versao':1});j=esperar(app,'pagina_job',job['id'])
            expected=name not in ('invalida','larga');assert (j['estado']=='concluida')==expected,(name,j)
            if expected:
                pdf=app._paginas.arquivos(j['id'],'pdf')[0][1];reader=PdfReader(pdf);assert all(page.extract_text().strip() for page in reader.pages)
                assert title in reader.pages[0].extract_text();assert len(app._paginas.arquivos(j['id'],'png'))==len(reader.pages)
                if name=='longa':assert len(reader.pages)>1
                report.append({'caso':name,'estado':j['estado'],'pdf':str(pdf),'folhas':len(reader.pages)})
            else:report.append({'caso':name,'estado':j['estado'],'erro':j['erro']});assert not (app._paginas.exportacoes/j['id']).exists()
        specs=[('parabola','math_executar','math_obter',dict(expressao='x^2-4*x+3',inicio='-2',fim='6',ponto='3',operacoes=['grafico','derivada','criticos','tangente'])),('relacao','discreta_executar','discreta_obter',dict(tipo='relacoes',sobre=True,A='{1,2,3}',R='{(1,1),(1,2),(2,1),(2,3)}')),('verdade64','discreta_executar','discreta_obter',dict(tipo='logica',expressao='p&q&r&s&t&u',comparar='~(~p|~q|~r|~s|~t|~u)'))]
        for name,op,get,spec in specs:
            calc=app.executar(op,{'conversa':cid,'spec':spec});r=esperar(app,get,calc['id']);assert r['estado']=='concluida',r
            p=app.executar('pagina_criar',{'caderno':None});content=nova({'parabola':'Derivada, mínimo e reta tangente','relacao':'Relações: propriedades e contraexemplos','verdade64':'Tabela-verdade de seis variáveis'}[name]);app.executar('pagina_rascunho',{'id':p['id'],'conteudo':content,'revisao':p['revisao']});app.executar('pagina_calculo',{'id':p['id'],'calculo':calc['id']});app.executar('pagina_salvar',{'id':p['id']})
            job=app.executar('pagina_exportar',{'id':p['id'],'versao':1});j=esperar(app,'pagina_job',job['id']);assert j['estado']=='concluida',j
            pdf=app._paginas.arquivos(j['id'],'pdf')[0][1];reader=PdfReader(pdf);assert all(page.extract_text().strip() for page in reader.pages)
            report.append({'caso':name,'estado':j['estado'],'pdf':str(pdf),'folhas':len(reader.pages)})
        (ROOT/'relatorio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:app.fechar();app._executor.shutdown(wait=True)

if __name__=='__main__':main()
