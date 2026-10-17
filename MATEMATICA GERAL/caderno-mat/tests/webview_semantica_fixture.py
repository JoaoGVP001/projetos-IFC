"""Janela Qt e acervo fictício para testar a busca híbrida sem chaves."""
import os,sys,time,json
from pathlib import Path
from threading import Thread
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.desktop import abrir
from tutor_calculo.servico import Aplicacao
from tutor_calculo.piloto_local import isolamento
from tutor_calculo.materiais import Extracao

if __name__=='__main__':
    pasta=Path(os.environ['CADERNOMAT_TEST_DIR']);runtime=None
    if os.environ.get('CADERNOMAT_REAL_SEMANTICA')!='1':
        from test_semantica import RuntimeEmbedding
        runtime=RuntimeEmbedding();url=runtime.url
    else:
        url='http://127.0.0.1:11434';(pasta/'isolamento.json').write_text(json.dumps(isolamento()))
    app=Aplicacao(pasta/'historico.sqlite3')
    with app._banco() as (h,c,b):
        if not h.listar():
            bid=c.criar('Cálculo — teste');cid=h.criar(bid);c.salvar_navegacao(bid,cid)
            p=pasta/'apostila.txt';p.write_text('A derivada mede a taxa instantânea de variação. Geometricamente seu valor é o coeficiente angular da reta tangente ao gráfico.')
            mid,_=b.adicionar_arquivo(p,cid);b.processar(mid);b.associar_cadernos(mid,[bid]);b.vincular(mid,cid,False)
            other=h.criar();p=pasta/'outra.txt';p.write_text('Uma implicação é falsa quando a premissa é verdadeira e a conclusão é falsa.')
            m,_=b.adicionar_arquivo(p,other);b.processar(m)
        with h.db:h.db.execute('UPDATE semantica_config SET url=? WHERE id=1',(url,))
    def finalizar():
        import webview
        while not (pasta/'sair').exists():time.sleep(.1)
        webview.windows[0].destroy()
    Thread(target=finalizar,daemon=True).start()
    def proibido(*args,**kwargs):raise AssertionError('API online acionada.')
    try:
        with patch('openai.OpenAI',side_effect=proibido),patch('tutor_calculo.gemini.consultar',side_effect=proibido), \
             patch('tutor_calculo.servico.configuracao',return_value=('','online-inativo')),patch('tutor_calculo.servico.provedor_ativo',return_value='gemini'):
            abrir(app)
    finally:
        if runtime:runtime.close()
