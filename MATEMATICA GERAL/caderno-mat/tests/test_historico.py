import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tutor_calculo.armazenamento import Historico
from tutor_calculo.ia import limitar_contexto, perguntar
from tutor_calculo.gemini import consultar



class HistoricoTest(unittest.TestCase):
    def test_reinicio_isolamento_e_rascunho(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho=Path(pasta)/'historico.sqlite3'
            banco=Historico(caminho)
            a,b=banco.criar(),banco.criar()
            banco.adicionar(a,'user','Derive x^2')
            banco.adicionar(a,'assistant','2x')
            banco.adicionar(b,'user','Conjuntos')
            banco.renomear(a,'Derivadas')
            banco.rascunho(b,'Pergunta incompleta')
            banco.fechar()
            banco=Historico(caminho)
            self.assertEqual([m['texto'] for m in banco.mensagens(a)],['Derive x^2','2x'])
            self.assertEqual(len(banco.mensagens(b)),1)
            self.assertEqual(next(c for c in banco.listar() if c['id']==b)['rascunho'],'Pergunta incompleta')
            self.assertEqual(next(c for c in banco.listar() if c['id']==a)['titulo'],'Derivadas')
            banco.fechar()

    def test_contexto_exclui_erro_e_usuario_sem_resposta(self):
        mensagens=[{'papel':'user','texto':'A'},{'papel':'assistant','texto':'B'},
                   {'papel':'user','texto':'C'},{'papel':'assistant','texto':'erro','estado':'erro'},
                   {'papel':'user','texto':'D'}]
        self.assertEqual(limitar_contexto(mensagens),[{'role':'user','content':'A'},{'role':'assistant','content':'B'}])
        self.assertEqual(limitar_contexto(mensagens,limite=1),[])

    def test_openai_recebe_papeis_e_mensagem_atual(self):
        with patch('tutor_calculo.ia.provedor_ativo',return_value='openai'), patch('tutor_calculo.ia.configuracao',return_value=('teste','modelo')), patch('openai.OpenAI') as cliente:
            api=cliente.return_value.__enter__.return_value
            api.responses.create.return_value=Mock(output_text='Resposta',status='completed')
            perguntar('Explique B', historico=[{'papel':'user','texto':'A'},{'papel':'assistant','texto':'B'}])
            self.assertEqual(api.responses.create.call_args.kwargs['input'],[{'role':'user','content':'A'},{'role':'assistant','content':'B'},{'role':'user','content':'Explique B'}])

    def test_gemini_recebe_contexto(self):
        import io,json
        with patch('tutor_calculo.gemini.urlopen',return_value=io.BytesIO(b'{"candidates":[{"content":{"parts":[{"text":"OK"}]},"finishReason":"STOP"}]}')) as api:
            consultar('teste','gemini-3.8-flash','Continue','Tutor',historico=[{'role':'user','content':'A'},{'role':'assistant','content':'B'}])
            dados=json.loads(api.call_args.args[0].data)
            self.assertEqual([m['role'] for m in dados['contents']],['user','model','user'])

if __name__=='__main__':
    unittest.main()
