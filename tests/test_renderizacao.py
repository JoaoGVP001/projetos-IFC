import unittest
try:
    from tutor_calculo.renderizacao import partes, imagem_formula, formula_legivel
except ImportError:
    partes = None


@unittest.skipIf(partes is None, 'Renderizacao Tk legada exige requirements-legado.txt e Tkinter')
class RenderizacaoTest(unittest.TestCase):
    def test_markdown_e_delimitadores(self):
        tokens=list(partes('Texto **forte** $x^2$\n$$\\frac{1}{2}$$ \\(y=2x\\) `codigo`'))
        self.assertIn(('negrito','forte'), tokens)
        self.assertIn(('formula','x^2'), tokens)
        self.assertIn(('formula_bloco',r'\frac{1}{2}'), tokens)
        self.assertIn(('formula','y=2x'), tokens)
        self.assertIn(('codigo','codigo'), tokens)

    def test_formulas_do_exercicio_renderizam(self):
        for formula in [r'f(x)=x^2-4x+3',r"f'(x)=2x-4",r'\mathbb{R}',r'\frac{d}{dx}[x^n]=nx^{n-1}',r'(-\infty,2)',r'2x=4\implies x=2',r'\text{Dom}(f)=\mathbb{R}']:
            with self.subTest(formula=formula):
                self.assertGreater(imagem_formula(formula,400).width,0)

    def test_formula_longa_cabe_no_painel(self):
        self.assertLessEqual(imagem_formula('x+'*100+'1',300).width,300)

    def test_notacao_nao_suportada_tem_texto_legivel(self):
        with self.assertRaises(ValueError):
            imagem_formula(r'\begin{align}x=1\end{align}',400)
        self.assertEqual(formula_legivel(r'x\geq 2'), 'x≥ 2')


if __name__=='__main__':
    unittest.main()
