"""Worker isolado de extracao. Falhas de bibliotecas nativas nao derrubam a janela."""

from pathlib import Path
import sys

from .armazenamento import Historico
from .materiais import Biblioteca


def main():
    if len(sys.argv) != 3:
        return 2
    banco = Historico(Path(sys.argv[1]))
    try:
        Biblioteca(banco).processar(sys.argv[2])
    finally:
        banco.fechar()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
