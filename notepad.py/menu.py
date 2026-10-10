"""Interface de linha de comando para o caderno de notas."""

from __future__ import annotations

from enum import Enum
from typing import Callable

from notas import CadernoDeNotas, Nota


class OpcoesComando(str, Enum):
    """Códigos aceitos pelo menu principal."""

    MOSTRAR_NOTAS = "1"
    PESQUISAR_NOTAS = "2"
    ADICIONAR_NOTA = "3"
    MODIFICAR_MEMO = "4"
    MODIFICAR_TAGS = "5"
    SAIR = "6"


class Menu:
    """Exibe o menu e encaminha cada escolha à lógica do caderno."""

    def __init__(self) -> None:
        self.caderno = CadernoDeNotas()
        self._executando = True
        self._acoes: dict[OpcoesComando, Callable[[], None]] = {
            OpcoesComando.MOSTRAR_NOTAS: self.mostrar_notas,
            OpcoesComando.PESQUISAR_NOTAS: self.pesquisar_notas,
            OpcoesComando.ADICIONAR_NOTA: self.adicionar_nota,
            OpcoesComando.MODIFICAR_MEMO: self.modificar_memo,
            OpcoesComando.MODIFICAR_TAGS: self.modificar_tags,
            OpcoesComando.SAIR: self.sair,
        }

    def executar(self) -> None:
        """Mantém o menu ativo até o usuário escolher sair."""

        print("Caderno de Notas")
        try:
            while self._executando:
                self._mostrar_menu()
                escolha = input("Escolha uma opção: ").strip()
                try:
                    opcao = OpcoesComando(escolha)
                except ValueError:
                    print("Opção inválida. Tente novamente.\n")
                    continue
                self._acoes[opcao]()
        except (EOFError, KeyboardInterrupt):
            print("\nPrograma encerrado.")

    @staticmethod
    def _mostrar_menu() -> None:
        print(
            "\n"
            "1 - Mostrar todas as notas\n"
            "2 - Pesquisar notas\n"
            "3 - Adicionar nota\n"
            "4 - Modificar texto de uma nota\n"
            "5 - Modificar tags de uma nota\n"
            "6 - Sair"
        )

    def mostrar_notas(self) -> None:
        self._exibir_notas(self.caderno.notas)

    def pesquisar_notas(self) -> None:
        filtro = input("Termo de pesquisa: ").strip()
        self._exibir_notas(self.caderno.pesquisar(filtro))

    def adicionar_nota(self) -> None:
        memo = input("Texto da nota: ").strip()
        tags = input("Tags (opcional): ").strip()
        nota = self.caderno.nova_nota(memo, tags)
        print(f"Nota {nota.id} adicionada.")

    def modificar_memo(self) -> None:
        id_nota = self._ler_id()
        if id_nota is None:
            return
        novo_memo = input("Novo texto: ").strip()
        if self.caderno.modificar_memo(id_nota, novo_memo):
            print("Texto modificado.")
        else:
            print("Nota não encontrada.")

    def modificar_tags(self) -> None:
        id_nota = self._ler_id()
        if id_nota is None:
            return
        novas_tags = input("Novas tags: ").strip()
        if self.caderno.modificar_tags(id_nota, novas_tags):
            print("Tags modificadas.")
        else:
            print("Nota não encontrada.")

    def sair(self) -> None:
        self._executando = False
        print("Até logo!")

    @staticmethod
    def _ler_id() -> int | None:
        valor = input("ID da nota: ").strip()
        try:
            return int(valor)
        except ValueError:
            print("O ID deve ser um número inteiro.")
            return None

    @staticmethod
    def _exibir_notas(notas: list[Nota]) -> None:
        if not notas:
            print("Nenhuma nota encontrada.")
            return

        for nota in notas:
            tags = nota.tags or "sem tags"
            data = nota.data_criacao.strftime("%d/%m/%Y")
            print(f"\n[{nota.id}] {nota.memo}")
            print(f"    Tags: {tags}")
            print(f"    Criada em: {data}")


if __name__ == "__main__":
    Menu().executar()
