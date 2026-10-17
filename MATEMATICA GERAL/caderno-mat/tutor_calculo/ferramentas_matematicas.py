"""Motor L3 restrito. Executado em subprocesso; não acessa banco, rede ou arquivos."""
import base64
import io
import json
import math
import re
import sys

import sympy as sp
from sympy.calculus.util import continuous_domain
from .matematica import X, expressao

VERSAO = 'matematica-v1'
OPERACOES = ('grafico', 'derivada', 'valor', 'tangente', 'criticos', 'integral', 'area')
MAX_AMOSTRAS = 700
MAX_PNG = 2_000_000


def validar_spec(d, *, incompleta=False):
    if not isinstance(d, dict) or set(d) - {'expressao', 'inicio', 'fim', 'ponto', 'operacoes'}:
        raise ValueError('Parâmetros matemáticos desconhecidos.')
    out = {}
    for campo in ('expressao', 'inicio', 'fim', 'ponto'):
        valor = d.get(campo, '')
        if incompleta and valor is None: valor = ''
        if not isinstance(valor, str) or len(valor) > (300 if campo == 'expressao' else 80) or '\x00' in valor:
            raise ValueError('Use textos curtos para a função, intervalo e ponto.')
        out[campo] = valor.strip()
    ops = d.get('operacoes')
    if not isinstance(ops, list) or not 1 <= len(ops) <= len(OPERACOES) or any(not isinstance(o, str) or o not in OPERACOES for o in ops) or len(set(ops)) != len(ops):
        raise ValueError('Escolha operações matemáticas registradas, sem repetições.')
    out['operacoes'] = ops
    if not incompleta and (not out['expressao'] or not out['inicio'] or not out['fim']):
        raise ValueError('Informe a função e os dois limites do intervalo.')
    if not incompleta and any(o in ops for o in ('valor', 'tangente')) and not out['ponto']:
        raise ValueError('Informe o ponto para calcular o valor ou a tangente.')
    return out


def constante(texto):
    n = expressao(texto)
    if n.free_symbols or n.is_real is not True or n.is_finite is not True or abs(n) > 10_000:
        raise ValueError('Use uma constante real finita entre -10000 e 10000.')
    return n


def parametros_do_pedido(result, pedido):
    """Copiar dados explícitos; valores inventados pelo modelo nunca preenchem campos."""
    if not isinstance(pedido, str) or len(pedido) > 1500: raise ValueError('Pedido inválido.')
    pedido = pedido.replace('²', '^2').replace('³', '^3').replace('−', '-')
    funcs = list(re.finditer(r'f\s*\(\s*x\s*\)\s*=', pedido, re.I))
    func = re.search(r'f\s*\(\s*x\s*\)\s*=\s*([^;\n]+)', pedido, re.I) if len(funcs) == 1 else None
    expr = re.split(r'\s+(?:no|em|com|intervalo|e\s+a\s+tangente)\b', func[1], maxsplit=1, flags=re.I)[0].strip() if func else ''
    # Aceita a notação escolar 4x, preservando o texto/denominadores originais.
    expr = re.sub(r'(\d)\s*x\b', r'\1*x', expr)
    try:
        if expr: expressao(expr, preservar=True); expressao(expr)
    except ValueError: expr = ''
    result['expressao'] = expr
    intervals = list(re.finditer(r'\[\s*([^\[\](),;]{1,80}),\s*([^\[\](),;]{1,80})\s*\]', pedido))
    if not intervals:
        intervals = list(re.finditer(r'intervalo\s*:?\s*\(\s*([^(),;]{1,80}),\s*([^(),;]{1,80})\s*\)', pedido, re.I))
    interval = intervals[0] if len(intervals) == 1 else None
    result['inicio'] = interval[1].strip() if interval else ''
    result['fim'] = interval[2].strip() if interval else ''
    points = list(re.finditer(r'\bx\s*=\s*', pedido, re.I))
    result['ponto'] = re.split(r'\s+(?:e|no|em|com|para)\b', re.split(r'[;\n,]', pedido[points[0].end():],maxsplit=1)[0],maxsplit=1,flags=re.I)[0].strip().rstrip('.') if len(points) == 1 else ''
    if len(points) == 1 and re.match(r'\s*[+-]?\d+,\d', pedido[points[0].end():]): result['ponto'] = ''
    for k in ('inicio','fim','ponto'):
        if result[k]:
            try: constante(result[k])
            except ValueError: result[k] = ''
    return result


def numero(n):
    try: f = float(n.evalf(15))
    except (TypeError, ValueError, OverflowError): return None
    return f if math.isfinite(f) and abs(f) <= 1e100 else None


def dado(n):
    return {'texto': str(n), 'latex': sp.latex(n), 'aproximacao': numero(n)}


def dominio_original(raw, intervalo):
    # Intersectar subexpressões também preserva log/denominadores cancelados.
    domain = intervalo
    vistos = set()
    for no in sp.preorder_traversal(raw):
        if not isinstance(no, sp.Expr) or not no.has(X) or no in vistos: continue
        vistos.add(no)
        domain = domain.intersect(continuous_domain(no, X, intervalo))
    return domain


def intervalos(domain):
    if domain is sp.S.EmptySet: return []
    if isinstance(domain, sp.Interval): return [domain]
    if isinstance(domain, sp.Union):
        parts = list(domain.args)
        if all(isinstance(p, sp.Interval) for p in parts) and len(parts) <= 40:
            return sorted(parts, key=lambda p: float(p.start))
    raise ValueError('Não foi possível separar este domínio em até 40 intervalos. Reduza o intervalo ou simplifique a função.')


def criticos(f, domain, a, b, global_domain):
    if domain != sp.Interval(a, b) or not f.is_polynomial(X) or sp.degree(f, X) > 4:
        raise ValueError('Pontos críticos: suporte inicial a polinômios de grau até 4, definidos em todo o intervalo.')
    deriv = sp.diff(f, X)
    if deriv == 0:
        return {'tipo': 'criticos', 'estado': 'simbolico', 'texto': 'Função constante: todos os pontos são críticos; mínimo e máximo coincidem.', 'valor': dado(f)}
    roots = sp.solveset(deriv, X, domain=sp.S.Reals)
    if not isinstance(roots, sp.FiniteSet): raise ValueError('Conjunto de pontos críticos fora do escopo.')
    if any(r.is_real is not True or numero(r) is None for r in roots): raise ValueError('Não foi possível ordenar os pontos críticos.')
    allroots = sorted(roots, key=float)
    points = []
    for i, r in enumerate(allroots):
        left = (allroots[i-1]+r)/2 if i else r-1
        right = (allroots[i+1]+r)/2 if i+1 < len(allroots) else r+1
        sl, sr = sp.sign(deriv.subs(X, left)), sp.sign(deriv.subs(X, right))
        if sl not in (-1, 1) or sr not in (-1, 1): raise ValueError('Sinal da derivada não determinado; classificação não verificada.')
        tipo = 'mínimo local' if sl == -1 and sr == 1 else 'máximo local' if sl == 1 and sr == -1 else 'estacionário sem extremo'
        if bool(a <= r <= b): points.append({'x': dado(r), 'y': dado(f.subs(X, r)), 'classificacao': tipo})
    candidatos = [(a, f.subs(X, a)), (b, f.subs(X, b))] + [(r, f.subs(X, r)) for r in roots if bool(a < r < b)]
    minval, maxval = sp.Min(*(p[1] for p in candidatos)), sp.Max(*(p[1] for p in candidatos))
    mins = [p for p in candidatos if sp.simplify(p[1]-minval) == 0]
    maxs = [p for p in candidatos if sp.simplify(p[1]-maxval) == 0]
    if not mins or not maxs: raise ValueError('Ordem dos valores não determinada simbolicamente; extremos não verificados.')
    minimo, maximo = mins[0], maxs[0]
    out = {'tipo': 'criticos', 'estado': 'simbolico', 'pontos': points,
           'minimo_intervalo': {'x': dado(minimo[0]), 'y': dado(minimo[1])},
           'maximo_intervalo': {'x': dado(maximo[0]), 'y': dado(maximo[1])},
           'minimos_intervalo': [{'x':dado(p[0]),'y':dado(p[1])} for p in mins],
           'maximos_intervalo': [{'x':dado(p[0]),'y':dado(p[1])} for p in maxs]}
    # Polinômio de grau par e sinal dominante: extremos absolutos em R.
    grau = sp.degree(f, X)
    if grau % 2 == 0 and allroots and global_domain == sp.S.Reals:
        candidatos_r = [(r, f.subs(X, r)) for r in allroots]
        positivo = sp.Poly(f, X).LC().is_positive
        if positivo is None: raise ValueError('Sinal dominante não determinado; extremo absoluto não verificado.')
        valor_extremo = (sp.Min if positivo else sp.Max)(*(p[1] for p in candidatos_r))
        extremos = [p for p in candidatos_r if sp.simplify(p[1]-valor_extremo)==0]
        if not extremos: raise ValueError('Extremo absoluto não determinado simbolicamente.')
        extremo = extremos[0]
        out['minimo_absoluto' if positivo else 'maximo_absoluto'] = {'x': dado(extremo[0]), 'y': dado(extremo[1]), 'dominio': 'Reais'}
        out['extremos_absolutos'] = [{'x':dado(p[0]),'y':dado(p[1])} for p in extremos]
    return out


def integral(f, domain, a, b, area=False):
    # Suporte deliberado apenas a integrais próprias, sem valor principal.
    if domain != sp.Interval(a, b):
        raise ValueError('Integral imprópria ou com ponto fora do domínio. Esta versão não verifica convergência nem calcula valor principal.')
    integrando = sp.Abs(f) if area else f
    val = sp.integrate(integrando, (X, a, b))
    if not val.has(sp.Integral) and val.is_real is True and val.is_finite is True:
        return {'tipo': 'area' if area else 'integral', 'estado': 'simbolico', 'valor': dado(val), 'limites': [str(a), str(b)]}
    # Sem singularidades: evalf de Integral, não soma de poucos pixels.
    val = sp.Integral(integrando, (X, a, b)).evalf(12)
    if val.has(sp.Integral) or val.is_real is not True or numero(val) is None:
        raise ValueError('Não foi possível obter resultado finito; integral não verificada.')
    return {'tipo': 'area' if area else 'integral', 'estado': 'numerico', 'valor': dado(val), 'limites': [str(a), str(b)], 'precisao': '12 dígitos solicitados; sem certificação de erro'}


def tangente(f, raw, ponto):
    domain = dominio_original(raw, sp.S.Reals)
    if domain.contains(ponto) is not sp.S.true:
        raise ValueError('O ponto não pertence ao domínio real original.')
    if domain.boundary.contains(ponto) is not sp.S.false:
        raise ValueError('Ponto na fronteira do domínio; derivada bilateral não verificada.')
    value = f.subs(X, ponto)
    # Quociente incremental lateral detecta cúspides e pontos sem derivada.
    t = sp.Symbol('h', real=True)
    quotient = (f.subs(X, ponto+t)-value)/t
    left = sp.limit(quotient, t, 0, dir='-'); right = sp.limit(quotient, t, 0, dir='+')
    if left.is_real is not True or left.is_finite is not True or right.is_finite is not True or sp.simplify(left-right) != 0:
        raise ValueError('Derivada bilateral finita não existe neste ponto; tangente não verificada.')
    if numero(value) is None or numero(left) is None: raise ValueError('Valor ou inclinação fora dos limites.')
    line = sp.expand(value+left*(X-ponto))
    return {'tipo': 'tangente', 'estado': 'simbolico', 'ponto': {'x': dado(ponto), 'y': dado(value)}, 'inclinacao': dado(left), 'reta': dado(line)}, line


def amostrar(f, partes):
    segments = []
    for p in partes:
        a, b = float(p.start), float(p.end)
        n = max(8, MAX_AMOSTRAS // max(1, len(partes)))
        # Cada componente é independente; um domínio não comprovado é recusado.
        eps = max((b-a)*1e-4, 1e-10)
        a += eps if p.left_open else 0; b -= eps if p.right_open else 0
        if a >= b: continue
        xs, ys = [], []
        for i in range(n):
            x = a+(b-a)*i/(n-1)
            y = numero(f.subs(X, sp.Float(x)))
            if y is None:
                if xs: segments.append({'x': xs, 'y': ys}); xs, ys = [], []
            else: xs.append(x); ys.append(y)
        if xs: segments.append({'x': xs, 'y': ys})
    if not segments: raise ValueError('Nenhum valor real finito disponível para o gráfico.')
    return segments


def desenhar(f, segments, intervalo, partes, tangent=None, fill=False):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import numpy as np
    fig = Figure(figsize=(8, 4.8), dpi=120, layout='constrained'); FigureCanvasAgg(fig)
    ax = fig.add_subplot()
    ax.set_facecolor('#fafaf7'); fig.set_facecolor('#ffffff')
    for i, seg in enumerate(segments):
        ax.plot(seg['x'], seg['y'], color='#167665', lw=2, label='f(x)' if i == 0 else None)
        if fill: ax.fill_between(seg['x'], seg['y'], 0, alpha=.14, color='#167665')
    vals = [y for s in segments for y in s['y']]
    lo, hi = np.percentile(vals, [3, 97]); margin = max((hi-lo)*.18, 1)
    ax.set_ylim(float(lo-margin), float(hi+margin))
    ax.set_xlim(float(intervalo[0]), float(intervalo[1]))
    buracos = set()
    for part in partes:
        for endpoint, opened in [(part.start,part.left_open),(part.end,part.right_open)]:
            if not opened or endpoint in buracos: continue
            value = f.subs(X,endpoint)
            if value.has(sp.nan) and f.is_rational_function(X): value=sp.cancel(f).subs(X,endpoint)
            y = numero(value)
            if y is not None:
                ax.scatter([float(endpoint)], [y], facecolors='#ffffff', edgecolors='#167665', zorder=5)
                buracos.add(endpoint)
    if tangent:
        point, slope = tangent
        xs = [segments[0]['x'][0], segments[-1]['x'][-1]]
        ys = [float(point['y']['aproximacao'])+slope*(x-point['x']['aproximacao']) for x in xs]
        ax.plot(xs, ys, '--', color='#956323', label='Reta tangente', lw=1.6)
        ax.scatter([point['x']['aproximacao']], [point['y']['aproximacao']], color='#956323', zorder=4)
    ax.axhline(0, color='#89928d', lw=.7); ax.axvline(0, color='#89928d', lw=.7)
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.grid(alpha=.18); ax.legend()
    ax.set_title('Função e resultados locais')
    buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=120)
    raw = buf.getvalue()
    if len(raw) > MAX_PNG: raise ValueError('Gráfico excedeu o limite de 2 MB.')
    return base64.b64encode(raw).decode()


def calcular(spec):
    spec = validar_spec(spec)
    raw = expressao(spec['expressao'], preservar=True)
    f = expressao(spec['expressao'])
    a, b = constante(spec['inicio']), constante(spec['fim'])
    if a >= b or float(b-a) < 1e-6: raise ValueError('O início deve ser menor que o fim; largura mínima 0,000001.')
    try:
        domain = dominio_original(raw, sp.Interval(a, b))
        global_domain = dominio_original(raw, sp.S.Reals)
        partes = intervalos(domain)
    except (NotImplementedError, TypeError) as exc:
        raise ValueError('Domínio fora do escopo. Simplifique a função ou reduza o intervalo.') from exc
    if not partes: raise ValueError('Não há domínio real no intervalo solicitado.')
    from importlib.metadata import version
    out = {'versao': VERSAO, 'bibliotecas':{'sympy':sp.__version__,'matplotlib':version('matplotlib')}, 'expressao_original': spec['expressao'], 'normalizada': dado(f),
           'dominio': str(global_domain), 'dominio_latex': sp.latex(global_domain),
           'dominio_intervalo': str(domain), 'intervalo': [str(a), str(b)],
           'hipoteses': ['x real', 'Funções trigonométricas em radianos', 'Domínio preservado da expressão original'],
           'resultados': [], 'avisos': ['O gráfico usa amostras numéricas; não é uma prova. Escala vertical automática pode recortar valores próximos de polos.']}
    tangent = None
    for op in spec['operacoes']:
        if op == 'grafico': continue
        try:
            if op == 'derivada':
                derivative = sp.diff(f, X)
                if derivative.has(sp.Derivative): raise ValueError('Derivada não resolvida simbolicamente; fora do escopo.')
                out['resultados'].append({'tipo': op, 'estado': 'simbolico', 'valor': dado(derivative),
                    'nota': 'Expressão da derivada onde existe; cúspides e fronteiras exigem conferir derivabilidade no ponto.'})
            elif op == 'valor':
                p = constante(spec['ponto'])
                if global_domain.contains(p) is not sp.S.true: raise ValueError('O ponto não pertence ao domínio real original.')
                v = f.subs(X, p)
                if v.is_real is not True or v.is_finite is not True: raise ValueError('Valor real finito não verificado.')
                out['resultados'].append({'tipo': op, 'estado': 'simbolico', 'ponto': str(p), 'valor': dado(v)})
            elif op == 'tangente':
                result, _ = tangente(f, raw, constante(spec['ponto']))
                out['resultados'].append(result); tangent = (result['ponto'], result['inclinacao']['aproximacao'])
            elif op == 'criticos': out['resultados'].append(criticos(f, domain, a, b, global_domain))
            elif op in ('integral', 'area'): out['resultados'].append(integral(f, domain, a, b, op == 'area'))
        except (ValueError, NotImplementedError) as exc:
            out['resultados'].append({'tipo': op, 'estado': 'nao_verificado', 'aviso': str(exc)})
    segments = amostrar(f, partes)
    out['segmentos'] = segments
    if tangent and not a <= tangent[0]['x']['aproximacao'] <= b:
        out['avisos'].append('Ponto de tangência fora do intervalo exibido; confira as coordenadas no resultado.')
    out['png'] = desenhar(f, segments, (a,b), partes, tangent, any(o in spec['operacoes'] for o in ('integral', 'area')) and domain == sp.Interval(a,b))
    return out


def resumo(resultado):
    lines = ['### Cálculo local', f"Função original: `{resultado['expressao_original']}`", '$$f(x)='+resultado['normalizada']['latex']+'$$',
             'Intervalo: '+', '.join(resultado['intervalo']), 'Domínio original: $'+resultado['dominio_latex']+'$',
             'Hipóteses: '+'; '.join(resultado['hipoteses'])+'.']
    names = {'derivada': 'Derivada', 'valor': 'Valor no ponto', 'tangente': 'Reta tangente', 'integral': 'Integral definida (saldo)', 'area': 'Área geométrica', 'criticos': 'Pontos críticos e extremos'}
    for r in resultado['resultados']:
        state = {'simbolico': 'Calculado simbolicamente', 'numerico': 'Aproximação numérica', 'nao_verificado': 'Não verificado'}[r['estado']]
        lines.append('**'+names[r['tipo']]+' · '+state+'**')
        if 'aviso' in r: lines.append(r['aviso']); continue
        if 'valor' in r: lines.append('$$'+r['valor']['latex']+'$$')
        if 'reta' in r: lines.append('$$y='+r['reta']['latex']+'$$')
        if 'ponto' in r: lines.append('Ponto: '+json.dumps(r['ponto'], ensure_ascii=False) if isinstance(r['ponto'], str) else 'Ponto: $('+r['ponto']['x']['latex']+', '+r['ponto']['y']['latex']+')$')
        for p in r.get('pontos', []): lines.append(p['classificacao']+': $('+p['x']['latex']+', '+p['y']['latex']+')$')
        for key, title in [('minimo_intervalo','Mínimo no intervalo'),('maximo_intervalo','Máximo no intervalo'),('minimo_absoluto','Mínimo absoluto em R'),('maximo_absoluto','Máximo absoluto em R')]:
            if key in r:
                points = r.get('minimos_intervalo' if key=='minimo_intervalo' else 'maximos_intervalo' if key=='maximo_intervalo' else 'extremos_absolutos', [r[key]])
                lines.append(title+': '+', '.join('$('+p['x']['latex']+', '+p['y']['latex']+')$' for p in points))
        if r.get('texto'): lines.append(r['texto'])
        if r.get('nota'): lines.append(r['nota'])
        if r.get('precisao'): lines.append(r['precisao'])
    lines.extend(resultado['avisos'])
    lines.append('Estas verificações cobrem somente as operações acima; não avaliam uma explicação ou gabarito inteiro.')
    return '\n\n'.join(lines)


def main():
    try:
        if sys.platform == 'linux':
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (1_500_000_000, 1_500_000_000))
            resource.setrlimit(resource.RLIMIT_CPU, (22, 23))
        request = sys.stdin.read(5000)
        payload = json.loads(request)
        if isinstance(payload, dict) and set(payload) in ({'validar'}, {'validar','pedido'}):
            result = validar_spec(payload['validar'], incompleta=True)
            if result['expressao']: expressao(result['expressao'], preservar=True); expressao(result['expressao'])
            for k in ('inicio', 'fim', 'ponto'):
                if result[k]: constante(result[k])
            if 'pedido' in payload: result = parametros_do_pedido(result, payload['pedido'])
        else: result = calcular(payload)
        print(json.dumps({'ok': True, 'resultado': result}, ensure_ascii=False, allow_nan=False))
    except Exception as exc:
        msg = str(exc) if isinstance(exc, (ValueError, NotImplementedError)) else 'Falha no cálculo local; operação não verificada.'
        print(json.dumps({'ok': False, 'erro': msg[:1000]}, ensure_ascii=False))


if __name__ == '__main__': main()
