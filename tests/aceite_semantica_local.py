"""Piloto de recuperação em português, explícito, offline e com acervo fictício."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import tempfile
import time
from unittest.mock import patch
from tutor_calculo.armazenamento import caminho_banco
from tutor_calculo.servico import Aplicacao
from tutor_calculo.recuperacao import recuperar_chat
from tutor_calculo.piloto_local import isolamento,Monitor
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject,NumberObject

DOCS={
 'derivada':'A derivada mede a taxa de variação instantânea de uma função. Sua interpretação geométrica é o coeficiente angular da reta tangente ao gráfico.',
 'integral':'A integral definida acumula quantidades ao longo de um intervalo. Ela corresponde à área orientada entre a curva e o eixo horizontal.',
 'implicacao':'Uma implicação lógica é falsa somente quando a premissa é verdadeira e a conclusão é falsa. Nos demais casos o condicional é verdadeiro.',
 'bijeção':'Uma bijeção é uma função simultaneamente injetora e sobrejetora. Cada elemento do contradomínio tem exatamente uma preimagem.',
 'permutacao':'Uma permutação ordena todos os elementos distintos de um conjunto. Há n! ordenações de n objetos sem repetição.',
 'conjuntos':'A interseção de dois conjuntos contém os elementos comuns a ambos. A união contém todos os elementos de pelo menos um deles.',
 'limite':'O limite descreve o valor ao qual a função tende quando a variável se aproxima de um ponto, independentemente do valor da função no ponto.',
 'formulas':"Pela regra da potência, para f(x)=x^2 temos f'(x)=2*x. Para f(x)=sen(x), a derivada é cos(x).",
 'nao-matematica':'Uma receita de pão utiliza farinha, água e fermento. O preparo termina quando a massa cresce e assa no forno.',
}
CASES=[
 ('Como medir a velocidade de mudança em um instante?','derivada'),
 ('Como descobrir a inclinação de uma curva num ponto?','derivada'),
 ('Como calcular a quantidade acumulada entre dois valores?','integral'),
 ('Quando uma frase se-então fica errada?','implicacao'),
 ('Como saber se uma correspondência pareia perfeitamente os dois conjuntos?','bijeção'),
 ('De quantas formas podemos colocar todas as pessoas em fila?','permutacao'),
 ('Qual operação pega apenas o que pertence aos dois grupos?','conjuntos'),
 ('Como estudar a tendência perto de um valor sem substituir exatamente nele?','limite'),
 ('O que significa integral definida?','integral'),
 ('A tabela verdade da implicação lógica','implicacao'),
 ('Segundo a apostila, qual regra se aplica a x^2?','formulas'),
 ("Em qual material está f'(x)=2*x?",'formulas'),
]


def pdf_de_teste(path):
    writer=PdfWriter()
    for _ in range(8):writer.add_blank_page(width=595,height=842)
    font=writer._add_object(DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')}))
    page=writer.pages[-1];page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
    stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 40 760 Td (A derivada mede a taxa de variacao instantanea de uma funcao.) Tj 0 -18 Td (Seu valor e o coeficiente angular da reta tangente ao grafico.) Tj ET')
    page[NameObject('/Contents')]=writer._add_object(stream)
    with path.open('wb') as file:writer.write(file)


def executar():
    isolated=isolamento();assert all(isolated.values()),'Use o script com namespace sem rede externa.'
    def proibido(*args,**kwargs):raise AssertionError('Provedor online acionado na recuperação local.')
    report={'isolamento':isolated,'modelo':'qwen3-embedding:0.6b','cpu':True,'limiar':.35,'casos':[]}
    with tempfile.TemporaryDirectory(prefix='cadernomat-sem-real-') as tmp,patch('openai.OpenAI',side_effect=proibido),patch('tutor_calculo.gemini.consultar',side_effect=proibido), Monitor() as monitor:
        app=Aplicacao(Path(tmp)/'h.sqlite3');ids={}
        with app._banco() as (h,c,b):
            cid=h.criar();c.salvar_navegacao(None,cid)
            for name,content in DOCS.items():
                path=Path(tmp)/(name+'.txt');path.write_text(content)
                mid,_=b.adicionar_arquivo(path,cid);b.processar(mid);b.vincular(mid,cid,True);ids[name]=mid
            pdf=Path(tmp)/'apostila.pdf';pdf_de_teste(pdf);pdfid,_=b.adicionar_arquivo(pdf,cid);b.processar(pdfid)
        start=time.monotonic();app.executar('semantica_indexar',{'confirmado':True})
        while app.executar('estado',{})['ocupado']:
            assert time.monotonic()-start<180,'Tempo de indexação excedido.';time.sleep(.1)
        status=app.executar('semantica_status',{});assert status['trabalho']['estado']=='concluido',status
        report['indexacao_s']=round(time.monotonic()-start,3);report['indice']=status
        with app._banco() as (h,c,b):
            from tutor_calculo.semantica import IndiceSemantico
            index=IndiceSemantico(h)
            for query,expected in CASES:
                details={};start=time.monotonic();hits=index.candidatos(list(ids.values()),query,details)
                lexical=[f for f in b.recuperar(cid,query) if f['selecao']=='busca textual']
                report['casos'].append({'pergunta':query,'esperado':expected,'top1':next((k for k,v in ids.items() if hits and v==hits[0]['material_id']),None),
                    'hibrida_acertou_top1':bool(hits and hits[0]['material_id']==ids[expected]),
                    'textual_acertou_top1':bool(lexical and lexical[0]['material_id']==ids[expected]),
                    'latencia_s':round(time.monotonic()-start,3),'recuperacao':details,
                    'candidatos':[{'nome':f['nome'],'selecao':f['selecao'],'similaridade':f.get('similaridade')} for f in hits[:3]]})
            # Documento antigo já presente: escopo/IDs explícitos, sem reenviar original.
            b.vincular(pdfid,cid,True)
            for mid in ids.values():b.vincular(mid,cid,False)
            sources=recuperar_chat(b,cid,'inclinação de uma curva num ponto',{})
            assert sources and all(f['material_id']==pdfid for f in sources),sources
            assert sources[0]['pagina']==8
            report['pdf_pagina_verificada']=8
            b.excluir(pdfid)
            assert not recuperar_chat(b,cid,'inclinação de uma curva num ponto',{})
        app.fechar();app._executor.shutdown(wait=True);app=Aplicacao(Path(tmp)/'h.sqlite3')
        assert app.executar('semantica_status',{})['indexados']==len(ids)
        assert app.executar('estado',{})['conversa']['id']==cid
        app.fechar();app._executor.shutdown(wait=True)
        report['reinicio_e_exclusao_ok']=True
    report['amostras_recursos']=monitor.samples
    report['recursos_aviso']='RAM disponível e VRAM total do sistema; outros aplicativos podem contribuir. Embedding pediu num_gpu=0.'
    report['hibrida_top1']=sum(c['hibrida_acertou_top1'] for c in report['casos'])
    report['textual_top1']=sum(c['textual_acertou_top1'] for c in report['casos'])
    target=caminho_banco().parent/'ia-local/relatorios/l2-recuperacao-real.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2));target.chmod(0o600)
    print(f"Piloto offline: híbrida top1 {report['hibrida_top1']}/{len(CASES)}; textual top1 {report['textual_top1']}/{len(CASES)}; indexação {report['indexacao_s']}s. Não é certificação de qualidade geral.")
    print('PDF real extraído/página 8, exclusão e reinício OK. Relatório:',target)

if __name__=='__main__':executar()
