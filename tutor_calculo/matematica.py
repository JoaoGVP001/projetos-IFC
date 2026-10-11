"""Leitura e analise de funcoes por partes perto de um ponto."""

import ast
import math
import re
from dataclasses import dataclass

import sympy as sp


X = sp.Symbol("x", real=True)
FUNCOES = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
}
CONSTANTES = {"x": X, "pi": sp.pi, "e": sp.E}
OPERACOES = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
}


def expressao(texto: str, *, preservar=False):
    """Converte uma expressao aritmetica limitada, sem executar codigo Python."""
    if not isinstance(texto, str) or not texto.strip() or len(texto) > 300:
        raise ValueError('Use uma expressão de até 300 caracteres.')
    texto = re.sub(r"\bsen\b", "sin", texto.strip(), flags=re.IGNORECASE)
    texto = re.sub(r"\bsenx\b", "sin(x)", texto, flags=re.IGNORECASE)
    texto = texto.replace("^", "**").replace("π", "pi")
    try:
        arvore = ast.parse(texto, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError(f"Expressao invalida: {texto}") from exc

    nos = list(ast.walk(arvore))
    if len(nos) > 100:
        raise ValueError('Expressão complexa: limite de 100 nós.')
    def profundidade(no):
        return 1 + max((profundidade(f) for f in ast.iter_child_nodes(no)), default=0)
    if profundidade(arvore) > 16:
        raise ValueError('Expressão complexa: limite de profundidade 16.')
    for no in nos:
        if isinstance(no, ast.Constant) and type(no.value) in (int, float):
            if abs(no.value) > 1_000_000 or not math.isfinite(no.value):
                raise ValueError('Literal numérico não finito ou maior que 1 milhão.')

    def converter(no):
        if isinstance(no, ast.Constant) and type(no.value) in (int, float):
            return sp.Rational(str(no.value)) if isinstance(no.value, float) else sp.Integer(no.value)
        if isinstance(no, ast.Name) and no.id.lower() in CONSTANTES:
            return CONSTANTES[no.id.lower()]
        if isinstance(no, ast.BinOp) and type(no.op) in OPERACOES:
            a, b = converter(no.left), converter(no.right)
            if isinstance(no.op, ast.Pow):
                # Evita crescimento explosivo antes de construir a potência.
                if b.free_symbols or b.is_integer is not True or abs(b) > 12:
                    raise ValueError('Use expoente inteiro entre -12 e 12; para raiz quadrada use sqrt(x).')
                if isinstance(a, sp.Pow) and a.exp.is_number and abs(a.exp*b) > 12:
                    raise ValueError('Potências encadeadas excedem o limite de expoente efetivo 12.')
                if not a.free_symbols and (a.is_finite is not True or a.is_real is not True or abs(a) > sp.Integer(10)**100):
                    raise ValueError('Base constante fora dos limites permitidos.')
                if not a.free_symbols and b > 0 and abs(a)**b > sp.Integer(10)**100:
                    raise ValueError('Potência constante excede 100 dígitos.')
                return sp.Pow(a, b, evaluate=not preservar)
            if preservar:
                if isinstance(no.op, ast.Add): return sp.Add(a, b, evaluate=False)
                if isinstance(no.op, ast.Sub): return sp.Add(a, sp.Mul(-1, b, evaluate=False), evaluate=False)
                if isinstance(no.op, ast.Mult): return sp.Mul(a, b, evaluate=False)
                return sp.Mul(a, sp.Pow(b, -1, evaluate=False), evaluate=False)
            resultado = OPERACOES[type(no.op)](a, b)
            if not resultado.free_symbols and (resultado.is_finite is not True or abs(resultado) > sp.Integer(10)**100):
                raise ValueError('Resultado constante fora dos limites permitidos.')
            return resultado
        if isinstance(no, ast.UnaryOp) and isinstance(no.op, (ast.UAdd, ast.USub)):
            valor = converter(no.operand)
            return valor if isinstance(no.op, ast.UAdd) else -valor
        if (isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                and no.func.id.lower() in FUNCOES and len(no.args) == 1
                and not no.keywords):
            arg = converter(no.args[0])
            if not arg.free_symbols and (arg.is_real is not True or arg.is_finite is not True or abs(arg) > (100 if no.func.id.lower() == 'exp' else 1_000_000)):
                raise ValueError('Argumento constante fora dos limites permitidos.')
            resultado = FUNCOES[no.func.id.lower()](arg, evaluate=not preservar)
            if not arg.free_symbols and resultado.is_real is False:
                raise ValueError('Funções de constantes devem ter resultado real.')
            return resultado
        raise ValueError(f"Expressao nao suportada: {texto}. Use x, numeros, +, -, *, /, ^ e funcoes como sen(x).")

    resultado = converter(arvore.body)
    if resultado.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise ValueError('Expressão contém um valor não finito.')
    return resultado


@dataclass(frozen=True)
class Ramo:
    texto: str
    funcao: sp.Expr
    condicao: str


@dataclass(frozen=True)
class Problema:
    ponto: sp.Expr
    ramos: tuple[Ramo, ...]


_CONDICAO = re.compile(r"^x\s*(diferente\s+de|!=|<>|<=|>=|<|>|=|==|≠|≤|≥)\s*(.+)$", re.IGNORECASE)
_PONTO = re.compile(r"^(?:ponto\s*:\s*|em\s+)(?:x\s*=\s*)?(.+)$", re.IGNORECASE)


def ler_problema(texto: str) -> Problema:
    ramos = []
    ponto = None
    for linha in texto.splitlines():
        linha = linha.strip().rstrip("; ")
        if not linha or linha in ("}", "{") or re.match(r"^f\(x\)\s*=\s*\{?$", linha, re.IGNORECASE):
            continue
        if re.match(r"^(determine|verifique|analise|pergunta\s*:)", linha, re.IGNORECASE):
            continue
        encontrado = _PONTO.match(linha)
        if encontrado:
            ponto = expressao(encontrado.group(1))
            continue
        linha = linha.lstrip("{ ")
        partes = re.split(r",\s*(?:se\s+)?(?=x\s*(?:[!<>=≠≤≥]|diferente))", linha, maxsplit=1, flags=re.IGNORECASE)
        if len(partes) != 2:
            raise ValueError(f"Ramo nao reconhecido: {linha}. Use 'sen(x)/x, se x != 0'.")
        condicao = _CONDICAO.match(partes[1].strip())
        if not condicao:
            raise ValueError(f"Condicao nao reconhecida: {partes[1]}")
        limite_condicao = expressao(condicao.group(2))
        if limite_condicao.has(X):
            raise ValueError("A condicao deve comparar x com um numero.")
        operador = condicao.group(1).lower()
        operador = {"diferente de": "!=", "<>": "!=", "≠": "!=", "==": "=", "≤": "<=", "≥": ">="}.get(operador, operador)
        ramos.append((Ramo(partes[0].strip(), expressao(partes[0]), operador), limite_condicao))

    if ponto is None or ponto.has(X):
        raise ValueError("Informe o ponto em uma linha como 'em x = 0' ou 'ponto: 0'.")
    if len(ramos) < 2:
        raise ValueError("Informe pelo menos dois ramos da funcao.")
    if any(sp.simplify(limite - ponto) != 0 for _, limite in ramos):
        raise ValueError("Nesta versao, as condicoes dos ramos devem usar o ponto indicado.")
    return Problema(ponto, tuple(ramo for ramo, _ in ramos))


def _selecionar(ramos: tuple[Ramo, ...], lado: str) -> Ramo | None:
    aceitos = {
        "esquerda": {"<", "<=", "!="},
        "direita": {">", ">=", "!="},
        "ponto": {"=", "<=", ">="},
    }[lado]
    candidatos = [ramo for ramo in ramos if ramo.condicao in aceitos]
    if len(candidatos) > 1:
        raise ValueError(f"Ha mais de um ramo para {lado} do ponto.")
    return candidatos[0] if candidatos else None


def _igual(a, b) -> bool:
    return a == b or sp.simplify(a - b) == 0


def analisar_continuidade(problema: Problema) -> str:
    a = problema.ponto
    esquerdo = _selecionar(problema.ramos, "esquerda")
    direito = _selecionar(problema.ramos, "direita")
    no_ponto = _selecionar(problema.ramos, "ponto")
    if esquerdo is None or direito is None:
        raise ValueError("Falta um ramo a esquerda ou a direita do ponto.")

    lim_esq = sp.limit(esquerdo.funcao, X, a, dir="-")
    lim_dir = sp.limit(direito.funcao, X, a, dir="+")
    valor = no_ponto.funcao.subs(X, a) if no_ponto else None
    definido = valor is not None and valor.is_finite is True
    finitos = lim_esq.is_finite is True and lim_dir.is_finite is True
    limite_existe = finitos and _igual(lim_esq, lim_dir)

    linhas = [
        f"Analisando a continuidade em x = {a}:",
        f"1. Valor da funcao: f({a}) = {valor if definido else 'nao definido'}.",
        f"2. Pela esquerda, usamos {esquerdo.texto}: limite = {lim_esq}.",
        f"3. Pela direita, usamos {direito.texto}: limite = {lim_dir}.",
    ]
    if a == 0 and esquerdo.funcao == sp.sin(X) / X and direito.funcao == sp.sin(X) / X:
        linhas.append("   Aqui usamos o limite fundamental sen(x)/x -> 1 quando x -> 0 (em radianos).")
    if not finitos:
        linhas.append("4. Pelo menos um limite lateral e infinito ou indefinido. O limite finito nao existe; a funcao nao e continua.")
    elif not limite_existe:
        linhas.append("4. Os limites laterais sao diferentes. O limite bilateral nao existe; ha descontinuidade por salto.")
    elif not definido:
        linhas.append(f"4. Os limites laterais coincidem em {lim_esq}, mas f({a}) nao esta definido. Ha descontinuidade removivel.")
    elif _igual(lim_esq, valor):
        linhas.append(f"4. Os limites laterais coincidem em {lim_esq} e sao iguais a f({a}). A funcao e continua em x = {a}.")
    else:
        linhas.append(f"4. O limite bilateral e {lim_esq}, mas f({a}) = {valor}. A funcao nao e continua; a descontinuidade e removivel.")
    return "\n".join(linhas)
