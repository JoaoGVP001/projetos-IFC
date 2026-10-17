import unittest

from tutor_calculo.app import EXEMPLO
from tutor_calculo.matematica import analisar_continuidade, expressao, ler_problema


class ContinuidadeTest(unittest.TestCase):
    def test_exemplo_do_aluno(self):
        resposta = analisar_continuidade(ler_problema(EXEMPLO))
        self.assertIn("f(0) = 0", resposta)
        self.assertIn("esquerda, usamos sen(x)/x: limite = 1", resposta)
        self.assertIn("direita, usamos sen(x)/x: limite = 1", resposta)
        self.assertIn("nao e continua", resposta)

    def test_continua(self):
        texto = "f(x) = {\nx^2, se x != 2\n4, se x = 2\n}\nem x = 2"
        self.assertIn("A funcao e continua", analisar_continuidade(ler_problema(texto)))

    def test_salto(self):
        texto = "f(x) = {\nx+1, se x < 2\n5, se x = 2\nx^2, se x > 2\n}\nponto: 2"
        self.assertIn("descontinuidade por salto", analisar_continuidade(ler_problema(texto)))

    def test_enunciado_completo_e_abreviacao(self):
        texto = "Determine se a funcao e continua no ponto indicado:\nf(x) = {\nsenx/x, se x != 0\n0, se x = 0\n}\nPonto: x = 0"
        self.assertIn("descontinuidade e removivel", analisar_continuidade(ler_problema(texto)))

    def test_ramo_ausente(self):
        texto = "f(x) = {\nx, se x < 0\n0, se x = 0\n}\nem x = 0"
        with self.assertRaisesRegex(ValueError, "Falta um ramo"):
            analisar_continuidade(ler_problema(texto))

    def test_expressao_nao_executa_codigo(self):
        with self.assertRaises(ValueError):
            expressao("__import__('os').system('echo oi')")


if __name__ == "__main__":
    unittest.main()
