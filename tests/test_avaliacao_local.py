import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tutor_calculo.avaliacao_local import (PAGINA_FICTICIA, avaliar, destino_privado, executar,
                                          formato, gravar, resumo, validar_plano)
from tutor_calculo.provedores.contratos import ConsultaCancelada, RespostaIncompleta


def atividade(resposta='B'):
    return {'titulo': 'Soma', 'exercicios': [{'id': 'q1', 'enunciado': 'Quanto é 2+2?',
            'formato': 'escolha', 'resposta': resposta,
            'alternativas': [{'id': 'A', 'texto': '3'}, {'id': 'B', 'texto': '4.0'},
                             {'id': 'C', 'texto': '5'}, {'id': 'D', 'texto': '6'}]}]}


class Cliente:
    def __init__(self, config): self.config = config
    def metadados(self, route, **kwargs):
        if route == 'tags': return {'models': [{'name': 'teste:4b'}, {'name': 'outro:4b'}]}
        if route == 'ps': return {'models': []}
        if route == 'version': return {'version': 'simulado'}
        raise AssertionError('Operação fora do diagnóstico: '+route)


class AvaliacaoLocal(unittest.TestCase):
    def test_limites_modelos_consultas_perfis_e_contexto(self):
        good = [['teste:4b'], ['rapido'], ['inducao'], 1, 4096, 600, 180]
        self.assertEqual(validar_plano(*good)[0]['perfil'], 'rapido')
        for index, value in [(0, ['teste:4b']*2), (0, ['m:cloud']),
                             (1, ['inexistente']), (2, ['inducao']*2),
                             (3, True), (3, 4), (4, 8000), (5, 1801), (6, 0)]:
            bad = good.copy(); bad[index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError): validar_plano(*bad)
        with self.assertRaisesRegex(ValueError, '12 consultas'):
            validar_plano(['a:4b', 'b:4b'], ['rapido', 'estudo'], ['inducao','calculo'], 2, 4096, 600, 180)
        with self.assertRaises(ValueError):
            validar_plano(['a:4b'], ['completo'], ['inducao'], 1, 2048, 600, 180)

    def test_relatorio_fora_git_existentes_symlink_e_publicacao_atomica(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root); repo = base/'repo'; repo.mkdir(); (repo/'.git').write_text('gitdir: exemplo')
            with self.assertRaisesRegex(ValueError, 'Git'): destino_privado(repo/'report.json')
            dest = destino_privado(base/'privado'/'report.json'); gravar(dest, {'a': 1}); gravar(dest, {'a': 2})
            self.assertEqual(json.loads(dest.read_text()), {'a': 2})
            self.assertFalse(list(dest.parent.glob('.avaliacao-*')))
            if os.name != 'nt': self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ValueError, 'já existe'): destino_privado(dest)
            if os.name != 'nt':
                link = base/'atalho'; link.symlink_to(dest)
                with self.assertRaisesRegex(ValueError, 'simbólico'): destino_privado(link)

    def test_json_estrutura_nao_aprova_gabarito_errado_ou_narrativa(self):
        right = avaliar('atividade', json.dumps(atividade()))
        self.assertEqual(right['contrato'], 'valido'); self.assertTrue(all(right['checagens_pontuais'].values()))
        self.assertEqual(right['revisao_matematica'], 'pendente')
        wrong = avaliar('atividade', json.dumps(atividade('A')))
        self.assertEqual(wrong['contrato'], 'valido'); self.assertFalse(wrong['checagens_pontuais']['gabarito_numerico_4'])
        self.assertEqual(avaliar('atividade', '```json {}')['contrato'], 'invalido')
        other = atividade(); other['exercicios'][0]['enunciado'] = 'Quanto é 3+1?'
        self.assertFalse(avaliar('atividade', json.dumps(other))['checagens_pontuais']['pedido_2_mais_2'])

    def test_pagina_valida_e_formula_nunca_certificada_por_keywords(self):
        page = {'titulo': 'Estudo', 'assunto': '',
                'secoes': [{'id': 'resumo', 'titulo': '', 'texto': PAGINA_FICTICIA['secoes'][0]['texto']+' Uma identidade incorreta: $1=2$.', 'recurso': None}]}
        result = avaliar('pagina', json.dumps(page))
        self.assertEqual(result['contrato'], 'valido'); self.assertEqual(result['revisao_matematica'], 'pendente')
        narrative = avaliar('inducao', 'Caso base, hipótese, passo, conclusão: todos errados.\n```mermaid\ngraph LR')
        self.assertEqual(narrative['revisao_matematica'], 'pendente'); self.assertFalse(narrative['checagens_pontuais'])
        self.assertTrue(narrative['avisos'])
        self.assertNotIn('4', json.dumps(formato('atividade')))
        page['secoes'][0]['texto'] = 'Uma identidade alterada: $1+2=7$.'
        self.assertEqual(avaliar('pagina', json.dumps(page))['contrato'], 'invalido')
        self.assertFalse(avaliar('saudacao', 'a '*31)['checagens_pontuais']['ate_30_palavras'])

    def _run(self, dest, cases, answer):
        with patch('tutor_calculo.avaliacao_local.Ollama', Cliente), \
             patch('tutor_calculo.avaliacao_local.perguntar', side_effect=answer), \
             patch('tutor_calculo.piloto_local.isolamento', return_value={}), \
             patch('tutor_calculo.avaliacao_local.memoria', return_value={}):
            return executar(dest, ['teste:4b'], ['rapido'], cases, limite_s=600)

    def test_fachada_snapshot_sem_configuracao_pessoal_e_relatorio_por_tarefa(self):
        requests = []
        def answer(q, **kwargs):
            requests.append(kwargs)
            self.assertEqual(kwargs['provedor'], 'ollama'); self.assertNotIn('historico', kwargs)
            kwargs['metricas']({'segundos': 1, 'tokens_s': 3, 'digest': 'd', 'done_reason': 'stop'})
            return json.dumps(atividade()) if kwargs['modo'] == 'Gerar atividade' else 'Sete questões/23 minutos [M1].'
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root)/'resultado.json'
            result = self._run(dest, ['fontes', 'atividade'], answer)
            self.assertEqual(result['estado'], 'finalizada'); self.assertEqual(len(result['amostras']), 2)
            self.assertEqual(result, json.loads(dest.read_text()))
            source = requests[0]['preparada']; self.assertEqual(source['fontes'][0]['material_id'], 'ficticio-regulamento')
            self.assertIn('não', source['instrucoes']); self.assertIsNotNone(requests[1]['formato'])
            self.assertEqual(requests[1]['preparada']['orcamento']['reserva_saida'], 1024)
            self.assertEqual(result['amostras'][0]['dispositivo_antes']['estado'], 'nao_carregado')

    def test_erro_stream_preserva_parcial_metricas_sem_entrar_na_mediana(self):
        def answer(q, **kwargs):
            kwargs['trecho']('Texto parcial.'); kwargs['metricas']({'segundos': 2, 'motivo': 'limite_saida'})
            raise RespostaIncompleta('Limite.', 'limite_saida')
        with tempfile.TemporaryDirectory() as root:
            result = self._run(Path(root)/'resultado.json', ['inducao'], answer)
            row = result['amostras'][0]
            self.assertEqual(row['estado'], 'erro'); self.assertEqual(row['texto'], 'Texto parcial.')
            self.assertEqual(row['metricas']['motivo'], 'limite_saida')
            self.assertIsNone(result['resumo'][0]['segundos_mediana_concluidas'])

    def test_ctrl_c_checkpoint_e_nao_dispara_proxima_consulta(self):
        def answer(q, **kwargs): kwargs['trecho']('Parcial.'); raise KeyboardInterrupt()
        with tempfile.TemporaryDirectory() as root:
            result = self._run(Path(root)/'resultado.json', ['inducao', 'calculo'], answer)
            self.assertEqual(result['estado'], 'cancelada'); self.assertEqual(len(result['amostras']), 1)
            self.assertEqual(result['amostras'][0]['texto'], 'Parcial.')

    def test_limite_total_cancela_e_interrompe_rodada(self):
        class ImmediateTimer:
            def __init__(self, interval, callback): self.callback = callback
            def start(self): self.callback()
            def cancel(self): pass
        def answer(q, **kwargs): kwargs['cancelar'].verificar()
        with tempfile.TemporaryDirectory() as root, patch('tutor_calculo.avaliacao_local.Timer', ImmediateTimer):
            result = self._run(Path(root)/'resultado.json', ['inducao', 'calculo'], answer)
            self.assertEqual(result['estado'], 'limite_total'); self.assertEqual(len(result['amostras']), 1)

    def test_modelo_ausente_e_url_remota_recusados_antes_do_envio(self):
        with tempfile.TemporaryDirectory() as root, patch('tutor_calculo.avaliacao_local.Ollama', Cliente), \
             patch('tutor_calculo.avaliacao_local.perguntar') as query:
            with self.assertRaisesRegex(ValueError, 'download'):
                executar(Path(root)/'r.json', ['ausente:4b'], ['rapido'], ['inducao'])
            with self.assertRaises(ValueError):
                executar(Path(root)/'r.json', ['teste:4b'], ['rapido'], ['inducao'], url='http://example.com:11434')
            query.assert_not_called(); self.assertFalse((Path(root)/'r.json').exists())

    def test_metadados_invalidos_nao_disparam_consulta(self):
        with tempfile.TemporaryDirectory() as root, \
             patch('tutor_calculo.avaliacao_local.Ollama.metadados', return_value={'models': [None]}), \
             patch('tutor_calculo.avaliacao_local.perguntar') as query:
            with self.assertRaisesRegex(RuntimeError, 'Lista'):
                executar(Path(root)/'r.json', ['teste:4b'], ['rapido'], ['inducao'])
            query.assert_not_called()

    def test_orientacoes_por_tarefa_conservam_json_e_orcamento_2k(self):
        from tutor_calculo.ia import preparar_consulta
        local = {'perfil': 'rapido', 'contexto': 2048}
        corrected = preparar_consulta('Explique o limite.', modo='Corrigir', provedor='ollama', local=local)
        self.assertIn('domínio original', corrected['instrucoes'])
        b = corrected['orcamento']
        self.assertLessEqual(b['entrada_estimada']+b['reserva_saida']+b['margem'],2048)
        structured = preparar_consulta('Uma atividade simples.', modo='Gerar atividade', provedor='ollama', local={'perfil':'rapido','contexto':4096})
        self.assertIn('sem aspas decorativas', structured['instrucoes'])
        self.assertNotIn('palavras', structured['instrucoes'])
        self.assertEqual(structured['orcamento']['reserva_saida'],1024)
        from tutor_calculo.avaliacao_local import BLOCOS_FICTICIOS
        from tutor_calculo.organizacao import prompt_ids, plano_local
        labels=preparar_consulta(prompt_ids(BLOCOS_FICTICIOS),modo='Rotular blocos',provedor='ollama',local={'perfil':'rapido','contexto':4096})
        self.assertEqual(labels['orcamento']['reserva_saida'],1024)
        self.assertNotIn('palavras',labels['instrucoes'])
        valid=avaliar('rotulos',json.dumps(plano_local(BLOCOS_FICTICIOS)))
        self.assertEqual(valid['contrato'],'valido');self.assertEqual(valid['revisao_matematica'],'pendente')
        self.assertEqual(avaliar('rotulos','{"blocos":[]}')['contrato'],'invalido')

    def test_saudacao_nao_recebe_tarefa_de_aula_e_nao_engole_pedido(self):
        from tutor_calculo.ia import eh_saudacao, preparar_consulta
        self.assertTrue(eh_saudacao('Olá! Quero estudar matemática.'))
        induction=preparar_consulta('Olá, explique indução.',provedor='ollama',local={'perfil':'rapido','contexto':4096})
        self.assertIn('k arbitrário',induction['instrucoes']);self.assertNotIn('Extensão contínua',induction['instrucoes'])
        mixed=preparar_consulta('Explique indução e o limite de f(x).',provedor='ollama',local={'perfil':'rapido','contexto':4096})
        self.assertIn('k arbitrário',mixed['instrucoes']);self.assertIn('Extensão contínua',mixed['instrucoes'])
        limits=preparar_consulta('Explique indução e suas limitações.',provedor='ollama',local={'perfil':'rapido','contexto':4096})
        self.assertNotIn('Extensão contínua',limits['instrucoes'])
        for q in ('Olá, explique indução.', 'Bom dia, derive x^2.', 'Olá quero estudar matemática discreta'):
            self.assertFalse(eh_saudacao(q))
        p = preparar_consulta('Olá! Quero estudar matemática.', modo='Explicar', provedor='ollama', local={'perfil':'rapido','contexto':2048}, caderno={'nome':'Discreta','preferencia':'completa'})
        self.assertIn('apenas cumprimentar', p['instrucoes']); self.assertNotIn('Ao simplificar', p['instrucoes'])
        self.assertNotIn('Tarefa desta consulta: Explique', p['instrucoes'])
        self.assertNotIn('caso base', p['instrucoes'])


if __name__ == '__main__': unittest.main()
