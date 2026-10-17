"""Renderizacao local de Markdown basico e formulas, sem executar LaTeX."""

import io
import re
import tkinter as tk

from PIL import Image, ImageTk
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image

# Blocos matematicos precisam ter precedencia sobre formulas em linha.
TOKENS = re.compile(r'(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$|\*\*[^\n]+?\*\*|`[^`\n]+?`)')


def partes(texto):
    for token in TOKENS.split(texto):
        if not token:
            continue
        if token.startswith('$$') or token.startswith(r'\['):
            yield 'formula_bloco', token[2:-2].strip()
        elif token.startswith(r'\('):
            yield 'formula', token[2:-2].strip()
        elif token.startswith('$'):
            yield 'formula', token[1:-1].strip()
        elif token.startswith('**'):
            yield 'negrito', token[2:-2]
        elif token.startswith('`'):
            yield 'codigo', token[1:-1]
        else:
            yield 'texto', token


def imagem_formula(formula, largura):
    # Alguns comandos comuns de LaTeX nao fazem parte do MathText.
    formula = formula.replace(r'\dfrac', r'\frac').replace(r'\tfrac', r'\frac')
    formula = formula.replace(r'\implies', r'\Rightarrow').replace(r'\iff', r'\Leftrightarrow')
    formula = re.sub(r'\\(?:text|operatorname)\{([^{}]*)\}', lambda m: r'\mathrm{' + m[1].replace(' ', r'\ ') + '}', formula)
    buffer = io.BytesIO()
    math_to_image('$' + formula + '$', buffer, prop=FontProperties(size=15), dpi=130, format='png', color='#202B2A')
    buffer.seek(0)
    img = Image.open(buffer).convert('RGBA')
    # Formulas longas cabem na largura do painel sem scroll horizontal.
    if img.width > largura:
        img.thumbnail((largura, max(1, img.height)), Image.Resampling.LANCZOS)
    return img


def formula_legivel(formula):
    simbolos = {'infty':'∞', 'mathbb{R}':'ℝ', 'geq':'≥', 'leq':'≤', 'neq':'≠',
                'cdot':'·', 'times':'×', 'Rightarrow':'⇒', 'implies':'⇒', 'to':'→',
                'pi':'π', 'in':'∈', 'sqrt':'√', 'frac':'frac', 'left':'', 'right':''}
    for comando in sorted(simbolos, key=len, reverse=True):
        formula = formula.replace('\\' + comando, simbolos[comando])
    formula = re.sub(r'\\(?:text|mathrm|operatorname)\{([^{}]*)\}', r'\1', formula)
    return formula.replace('\\', '').strip()


class Renderizador:
    def __init__(self, textbox):
        self.texto = textbox
        self.imagens = []
        self.original = ''
        self.fallbacks = 0
        textbox.tag_configure('titulo', font=('DejaVu Sans', 19, 'bold'), spacing1=12, spacing3=7)
        textbox.tag_configure('subtitulo', font=('DejaVu Sans', 16, 'bold'), spacing1=10, spacing3=6)
        textbox.tag_configure('negrito', font=('DejaVu Sans', 15, 'bold'))
        textbox.tag_configure('codigo', font=('DejaVu Sans Mono', 13), background='#EDF3F1')
        textbox.tag_configure('formula_fallback', font=('DejaVu Sans Mono', 14))

    def mostrar(self, original):
        self.original = original
        self.fallbacks = 0
        self.imagens.clear()
        widget = self.texto
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        largura = max(240, widget.winfo_width() - 45)
        try:
            for tipo, conteudo in partes(original):
                if tipo.startswith('formula'):
                    try:
                        img = ImageTk.PhotoImage(imagem_formula(conteudo, largura), master=widget)
                        if tipo == 'formula_bloco':
                            widget.insert('end', '\n')
                        widget.image_create('end', image=img, align='center', padx=3, pady=5)
                        self.imagens.append(img)
                        if tipo == 'formula_bloco':
                            widget.insert('end', '\n')
                    except (ValueError, RuntimeError, tk.TclError):
                        self.fallbacks += 1
                        widget.insert('end', formula_legivel(conteudo), 'formula_fallback')
                elif tipo == 'texto':
                    for linha in conteudo.splitlines(keepends=True):
                        titulo = re.match(r'^\s{0,3}(#{1,6})\s+(.+?)(\n)?$', linha)
                        if titulo:
                            widget.insert('end', titulo[2] + ('\n' if titulo[3] else ''), 'titulo' if len(titulo[1]) <= 2 else 'subtitulo')
                        elif re.fullmatch(r'\s*[-*_]{3,}\s*', linha):
                            widget.insert('end', '\n' + '─' * 24 + '\n')
                        else:
                            widget.insert('end', re.sub(r'^(\s*)[*-]\s+', r'\1• ', linha))
                else:
                    widget.insert('end', conteudo, tipo)
            widget.yview_moveto(0)
        finally:
            widget.configure(state='disabled')
