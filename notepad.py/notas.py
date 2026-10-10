"""Classes de domínio do aplicativo de bloco de notas.

A lógica do caderno fica neste módulo para que outras interfaces, como uma
aplicação web ou gráfica, possam reutilizá-la sem depender do menu de terminal.
"""

from __future__ import annotations

from datetime import date


class Nota:
    """Representa uma anotação com texto, tags, data e identificador único."""

    _proximo_id = 1

    def __init__(self, memo: str, tags: str = "") -> None:
        self.memo = memo
        self.tags = tags
        self.data_criacao = date.today()
        self.id = Nota._proximo_id
        Nota._proximo_id += 1

    def corresp(self, filtro_pesquisa: str) -> bool:
        """Informa se o filtro aparece no texto ou nas tags da nota.

        A comparação não diferencia letras maiúsculas de minúsculas. Um filtro
        vazio corresponde a todas as notas, o que também permite listar o
        conteúdo completo do caderno por meio de ``pesquisar("")``.
        """

        filtro = filtro_pesquisa.casefold()
        return filtro in self.memo.casefold() or filtro in self.tags.casefold()


class CadernoDeNotas:
    """Gerencia uma coleção de objetos :class:`Nota`."""

    def __init__(self) -> None:
        self.notas: list[Nota] = []

    def nova_nota(self, memo: str, tags: str = "") -> Nota:
        """Cria uma nota, adiciona-a ao caderno e devolve o novo objeto."""

        nota = Nota(memo, tags)
        self.notas.append(nota)
        return nota

    def pesquisar(self, filtro: str) -> list[Nota]:
        """Devolve as notas cujo texto ou tags correspondem ao filtro."""

        return [nota for nota in self.notas if nota.corresp(filtro)]

    def modificar_memo(self, id_nota: int, memo: str) -> bool:
        """Altera o texto da nota indicada e informa se ela foi encontrada."""

        nota = self._encontrar_nota(id_nota)
        if nota is None:
            return False
        nota.memo = memo
        return True

    def modificar_tags(self, id_nota: int, tags: str) -> bool:
        """Altera as tags da nota indicada e informa se ela foi encontrada."""

        nota = self._encontrar_nota(id_nota)
        if nota is None:
            return False
        nota.tags = tags
        return True

    def _encontrar_nota(self, id_nota: int) -> Nota | None:
        """Busca internamente uma nota pelo identificador."""

        return next((nota for nota in self.notas if nota.id == id_nota), None)
