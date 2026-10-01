"""Interface de terminal do tutor."""

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


def resolver(texto: str) -> str:
    if "f(x)" in texto.lower() and ("se x" in texto.lower() or ", x" in texto.lower()):
        from .matematica import analisar_continuidade, ler_problema

        return analisar_continuidade(ler_problema(texto))
    return perguntar(texto)


def main() -> None:
    print("Tutor de Calculo 1")
    while True:
        print("\n1 - Resolver exercicio\n2 - Explicar conteudo ou corrigir tentativa\n3 - Testar exemplo de continuidade\n0 - Sair")
        try:
            opcao = input("Escolha: ").strip()
        except EOFError:
            break
        if opcao == "0":
            break
        if opcao not in {"1", "2", "3"}:
            print("Opcao invalida.")
            continue
        texto = EXEMPLO if opcao == "3" else ler_multilinha()
        if not texto:
            print("Digite uma questao para continuar.")
            continue
        try:
            print("\n" + (perguntar(texto) if opcao == "2" else resolver(texto)))
        except (ValueError, RuntimeError, ImportError) as exc:
            print(f"\nNao foi possivel resolver: {exc}")


if __name__ == "__main__":
    main()
