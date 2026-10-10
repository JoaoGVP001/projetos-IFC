"""Testes da lógica do caderno de notas."""

import unittest
from datetime import date

from notas import CadernoDeNotas, Nota


class TestNota(unittest.TestCase):
    def test_criacao_define_atributos_e_id_unico(self) -> None:
        primeira = Nota("Estudar POO", "python")
        segunda = Nota("Revisar UML")

        self.assertEqual(primeira.memo, "Estudar POO")
        self.assertEqual(primeira.tags, "python")
        self.assertEqual(primeira.data_criacao, date.today())
        self.assertEqual(segunda.id, primeira.id + 1)

    def test_corresp_ao_memo_ou_as_tags(self) -> None:
        nota = Nota("Entregar o projeto", "POO faculdade")

        self.assertTrue(nota.corresp("PROJETO"))
        self.assertTrue(nota.corresp("faculdade"))
        self.assertFalse(nota.corresp("matemática"))


class TestCadernoDeNotas(unittest.TestCase):
    def setUp(self) -> None:
        self.caderno = CadernoDeNotas()
        self.python = self.caderno.nova_nota("Praticar classes", "python poo")
        self.banco = self.caderno.nova_nota("Revisar SQL", "banco de dados")

    def test_nova_nota_e_pesquisa(self) -> None:
        self.assertEqual(len(self.caderno.notas), 2)
        self.assertEqual(self.caderno.pesquisar("python"), [self.python])
        self.assertEqual(self.caderno.pesquisar("revisar"), [self.banco])
        self.assertEqual(self.caderno.pesquisar(""), [self.python, self.banco])

    def test_modificar_memo(self) -> None:
        alterou = self.caderno.modificar_memo(self.python.id, "Estudar objetos")

        self.assertTrue(alterou)
        self.assertEqual(self.python.memo, "Estudar objetos")
        self.assertFalse(self.caderno.modificar_memo(-1, "não existe"))

    def test_modificar_tags(self) -> None:
        alterou = self.caderno.modificar_tags(self.banco.id, "sql dados")

        self.assertTrue(alterou)
        self.assertEqual(self.banco.tags, "sql dados")
        self.assertFalse(self.caderno.modificar_tags(-1, "não existe"))


if __name__ == "__main__":
    unittest.main()
