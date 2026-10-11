"""Correção determinística limitada; feedback de IA não vira nota objetiva."""
from decimal import localcontext
from .atividades import numero, texto


def respondida(r):
    v = r.get('resposta')
    return v is not None and (not isinstance(v, str) or bool(v.strip()))


def corrigir(q, r):
    if not respondida(r): return {'estado': 'sem_resposta', 'justificativa': 'Questão em branco; não foi contada como erro.'}
    v = r['resposta']; f = q['formato']
    if f == 'aberta': return {'estado': 'revisao_necessaria' if q['resposta'] else 'sem_gabarito', 'justificativa': 'Requer revisão manual ou feedback opcional de IA.'}
    if f == 'numerica':
        try:
            with localcontext() as ctx:
                ctx.prec = 250
                acerto = abs(numero(v)-numero(q['resposta'])) <= numero(q['tolerancia'])
        except ValueError: return {'estado': 'revisao_necessaria', 'justificativa': 'A resposta não é um decimal finito válido; nenhuma nota foi atribuída.'}
        regra = f"Diferença absoluta ≤ {q['tolerancia']}. Não interpreta expressões ou unidades."
    else:
        acerto = type(v) is type(q['resposta']) and v == q['resposta']; regra = 'Comparação com o gabarito registrado nesta versão.'
    return {'estado': 'correta' if acerto else 'incorreta', 'justificativa': regra}


def resumo(qs, respostas, finalizada=False):
    estados = [corrigir(q, respostas.get(q['id'], {}))['estado'] for q in qs] if finalizada else []
    acertos = estados.count('correta'); erros = estados.count('incorreta')
    return {'total': len(qs), 'respondidas': sum(respondida(respostas.get(q['id'], {})) for q in qs),
            'objetivas': acertos+erros, 'acertos': acertos, 'erros': erros,
            'nao_avaliadas': len(qs)-acertos-erros, 'dicas': sum(len(r.get('dicas', [])) for r in respostas.values()),
            'solucoes': sum(bool(r.get('revelada')) for r in respostas.values())}


def validar_resposta(q, v):
    if v is None: return None
    if q['formato'] == 'vf':
        if type(v) is not bool: raise ValueError('Escolha verdadeiro ou falso.')
    elif q['formato'] == 'escolha':
        if v not in [a['id'] for a in q['alternativas']]: raise ValueError('Alternativa inexistente.')
    else: v = texto(v, 8000)
    return v
