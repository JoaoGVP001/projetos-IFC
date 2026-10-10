"""Interface de terminal do tutor."""

import re

from .ia import perguntar


EXEMPLO = """f(x) = {
sen(x)/x, se x diferente de 0
0, se x = 0
}
em x = 0"""


def ler_multilinha() -> str:
    print("Digite a questao. Termine com uma linha em branco:")
    linhas = []
    while True:
        try:
            linha = input()
        except EOFError:
            break
        if not linha.strip():
            break
        linhas.append(linha)
    return "\n".join(linhas).strip()


def resolver(texto: str, usar_ia: bool = False, *, caderno=None, historico=None) -> str:
    contexto = {}
    if caderno is not None:
        contexto['caderno'] = caderno
    if historico is not None:
        contexto['historico'] = historico
    if usar_ia:
        return perguntar(texto, modo="Resolver", **contexto)
    normalizado = re.sub(r"\s+", "", texto.lower())
    if "f(x)" in normalizado and ("sex" in normalizado or ",x" in normalizado):
        from .matematica import analisar_continuidade, ler_problema

        return analisar_continuidade(ler_problema(re.sub(r"f\s*\(\s*x\s*\)", "f(x)", texto, flags=re.IGNORECASE)))
    return perguntar(texto, **contexto)


def main() -> None:
    print("CadernoMat — estudos de matematica")
    while True:
        print("\n1 - Resolver exercicio\n2 - Explicar conteudo ou corrigir tentativa\n3 - Testar exemplo de continuidade\n4 - Resolver com IA\n0 - Sair")
        try:
            opcao = input("Escolha: ").strip()
        except EOFError:
            break
        if opcao == "0":
            break
        if opcao not in {"1", "2", "3", "4"}:
            print("Opcao invalida.")
            continue
        texto = EXEMPLO if opcao == "3" else ler_multilinha()
        if not texto:
            print("Digite uma questao para continuar.")
            continue
        try:
            print("\n" + (perguntar(texto, modo="Explicar") if opcao == "2" else resolver(texto, usar_ia=opcao == "4")))
        except (ValueError, RuntimeError, ImportError) as exc:
            print(f"\nNao foi possivel resolver: {exc}")


if __name__ == "__main__":
    main()
