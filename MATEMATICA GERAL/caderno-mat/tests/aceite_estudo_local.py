"""Aceite explícito com pesos reais; dados fictícios e banco temporário."""
import json
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tutor_calculo.armazenamento import caminho_banco
from tutor_calculo.servico import Aplicacao
from tutor_calculo.piloto_local import isolamento, expressao_curta
from tutor_calculo.provedores.ollama import PADRAO


def executar():
    isolated=isolamento()
    assert all(isolated.values()),'Execute este aceite no namespace sem rede externa.'
    report={'isolamento':isolated,'modelo':PADRAO['modelo'],'consultas':[]}
    def proibido(*args,**kwargs):raise AssertionError('Provedor online acionado no aceite local.')
    with tempfile.TemporaryDirectory(prefix='cadernomat-estudo-real-') as tmp, \
         patch('openai.OpenAI',side_effect=proibido),patch('tutor_calculo.gemini.consultar',side_effect=proibido):
        app=Aplicacao(Path(tmp)/'h.sqlite3')
        app._ia_preferencias.salvar('ollama',PADRAO)
        def op(name,**args):return app.executar(name,args)
        def consultar(j):
            op('estudo_consultar',id=j['id'])
            deadline=time.monotonic()+240
            while time.monotonic()<deadline:
                result=op('estudo_job',id=j['id'])
                if result['estado']!='executando':
                    report['consultas'].append(result)
                    assert result['estado']=='concluida',result['erro']
                    return result
                time.sleep(.1)
            raise RuntimeError('Tempo do aceite de estudo excedido.')
        try:
            j=op('estudo_previa',tipo='geracao',assunto='Adição: quanto é 2+2? Alternativas e gabarito em números simples, sem LaTeX.',
                 quantidade=1,formatos=['escolha'],dificuldade='basica')
            done=consultar(j);assert op('atividades')['total']==0
            question=done['resultado']['exercicios'][0]
            value=next(a['texto'] for a in question['alternativas'] if a['id']==question['resposta'])
            # Alternativas aceitam Markdown/LaTeX no contrato do aplicativo.
            # O valor original permanece no relatório; removemos apenas um par
            # explícito de delimitadores matemáticos para conferir a conta.
            numeric=value.strip()
            if numeric.startswith('$') and numeric.endswith('$'):numeric=numeric[1:-1]
            report['gabarito_original']=value
            report['normalizacao_gabarito']='Remove somente delimitadores $...$ antes de avaliar o valor.'
            asked='2+2' in question['enunciado'].replace(' ','')
            report['enunciado_pedido_atendido']=asked
            try:correct=bool(expressao_curta(numeric)==4) if asked else None
            except (ValueError,SyntaxError):correct=False
            report['gabarito_2_mais_2_confere']=correct
            print(f'Geração real: esquema/validador aprovados; pedido 2+2: {asked}; gabarito: {correct}. Proposta não salva automaticamente.',flush=True)
            # O aceite funcional simula a revisão obrigatória do editor com uma
            # questão conhecida. Não mascara desvios do modelo: proposta bruta,
            # diagnóstico e alteração explícita permanecem no relatório.
            reviewed=deepcopy(done['resultado']);question=reviewed['exercicios'][0]
            question['enunciado']='Quanto é 2+2?';question['explicacao']='2+2=4.'
            option=next((a for a in question['alternativas'] if a['texto'].strip().strip('$')=='4'),None)
            if option is None:option=question['alternativas'][0];option['texto']='4'
            question['resposta']=option['id']
            report['revisao_explicita']='Antes de salvar no banco fictício, o teste define enunciado 2+2 e alternativa 4; isso não aprova a qualidade da proposta original.'
            activity=op('atividade_salvar',conteudo=reviewed,proposta=j['id'])
            attempt=op('tentativa_iniciar',atividade=activity['id'])
            op('tentativa_salvar',id=attempt['id'],exercicio=question['id'],resposta=question['resposta'],posicao=0)
            for kind in ('dica','feedback'):
                result=consultar(op('estudo_previa',tipo=kind,tentativa=attempt['id'],exercicio=question['id']))
                assert result['resultado']['provedor']=='ollama'
                print(kind+': resposta local persistida na tentativa.',flush=True)
            before=op('tentativa_obter',id=attempt['id'])
            app.fechar();app._executor.shutdown(wait=True);app=Aplicacao(Path(tmp)/'h.sqlite3')
            after=op('tentativa_obter',id=attempt['id'])
            assert before==after
            report['reinicio_preservado']=True
            print('Atividade, tentativa, dica e feedback preservados após reiniciar.',flush=True)
        finally:app.fechar();app._executor.shutdown(wait=True)
    target=caminho_banco().parent/'ia-local/relatorios/l1-estudo-real.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2));target.chmod(0o600)
    print('Relatório fictício salvo fora do Git:',target,flush=True)


if __name__=='__main__':executar()
