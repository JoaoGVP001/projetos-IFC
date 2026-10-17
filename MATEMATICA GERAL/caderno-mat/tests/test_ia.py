import os
import unittest
from unittest.mock import Mock, patch

from tutor_calculo.ia import perguntar


class IntegracaoIaTest(unittest.TestCase):
    def setUp(self):
        provedor = patch('tutor_calculo.ia.provedor_ativo', return_value='openai')
        provedor.start()
        self.addCleanup(provedor.stop)

    def test_exige_chave(self):
        with patch.dict(os.environ, {}, clear=True), patch("tutor_calculo.ia.dotenv_values", return_value={}):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                perguntar("O que e um limite?")

    def test_envia_pergunta_e_retorna_resposta(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave-de-teste", "OPENAI_MODEL": "modelo-teste"}, clear=True):
            with patch("tutor_calculo.ia.dotenv_values", return_value={}), patch("openai.OpenAI") as cliente:
                cliente.return_value.__enter__.return_value.responses.create.return_value = Mock(output_text="Explicacao em etapas", status="completed")
                self.assertEqual(perguntar("Calcule o limite"), "Explicacao em etapas")
                argumentos = cliente.return_value.__enter__.return_value.responses.create.call_args.kwargs
                self.assertEqual(argumentos["model"], "modelo-teste")
                self.assertEqual(argumentos["input"], "Calcule o limite")
                self.assertIn("passo a passo", argumentos["instructions"])

    def test_resposta_vazia_e_tratada(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave-de-teste"}, clear=True):
            with patch("tutor_calculo.ia.dotenv_values", return_value={}), patch("openai.OpenAI") as cliente:
                cliente.return_value.__enter__.return_value.responses.create.return_value = Mock(output_text="", status="completed")
                with self.assertRaisesRegex(RuntimeError, "nao retornou"):
                    perguntar("Explique derivadas")


if __name__ == "__main__":
    unittest.main()
