"""Ilustração local de indução: não é um verificador de demonstrações."""
import base64
from io import BytesIO
import json
import re
import sys
import textwrap
VERSAO='inducao-visual-v1'


def validar_spec(s):
    if not isinstance(s,dict) or set(s)-{'titulo','proposicao','inicio'}:raise ValueError('Dados da ilustração inválidos.')
    n=s.get('inicio',0)
    if type(n) is not int or not 0<=n<=100:raise ValueError('Use início inteiro entre zero e cem.')
    out={'inicio':n}
    for k,default,limit in [('titulo','Princípio de indução',80),('proposicao','P(n)',120)]:
        v=s.get(k,default)
        if not isinstance(v,str) or not v.strip() or len(v)>limit or any(c in v for c in '\n\r`$') or '![' in v or re.search(r'</?\w[^>]*>',v):raise ValueError('Use um rótulo curto em texto simples, sem código ou LaTeX.')
        out[k]=v.strip()
    return out


def resumo(r):
    s=r['dados'];return ('## Ilustração do princípio de indução\n\n'+s['titulo']+'\n\nProposição: '+s['proposicao']+'\n\n'
      +f"Caso base: P({s['inicio']}). Regra: para todo inteiro k ≥ {s['inicio']}, P(k) implica P(k+1).\n\n"
      +'A sequência com reticências é uma ilustração. Não verifica a proposição nem substitui a demonstração do caso base e da implicação para todo k.')


def renderizar(s):
    s=validar_spec(s)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import findfont
    from matplotlib.ft2font import FT2Font
    glyphs=FT2Font(findfont('DejaVu Sans')).get_charmap()
    if any(ord(c) not in glyphs for c in s['titulo']+s['proposicao']):raise ValueError('Símbolo indisponível na fonte local. Use texto simples nos rótulos.')
    from matplotlib.patches import FancyBboxPatch
    fig,ax=plt.subplots(figsize=(9,5.6),dpi=120);ax.set_xlim(0,9);ax.set_ylim(0,5.6);ax.axis('off');fig.patch.set_facecolor('#ffffff')
    ax.text(4.5,4.95,textwrap.fill(s['titulo'],36),ha='center',fontsize=15,color='#24332f')
    ax.text(4.5,4.2,textwrap.fill(s['proposicao'],50),ha='center',va='center',fontsize=11)
    labels=[f"Base\nP({s['inicio']})",'Hipótese\nP(k)', 'Passo\nP(k+1)']
    for x,label in zip([.6,3.5,6.4],labels):
        ax.add_patch(FancyBboxPatch((x,2.5),2,1,boxstyle='round,pad=0.12',edgecolor='#167665',facecolor='#e2f0e9'))
        ax.text(x+1,3,label,ha='center',va='center',fontsize=12)
    for x in [2.7,5.6]:ax.annotate('',xy=(x+.7,3),xytext=(x,3),arrowprops={'arrowstyle':'->','color':'#167665','lw':2})
    ax.text(4.5,1.85,f"Demonstrar: para todo inteiro k ≥ {s['inicio']}, P(k) ⇒ P(k+1)",ha='center',fontsize=12)
    ax.text(4.5,1.15,f"P({s['inicio']}) → P({s['inicio']+1}) → P({s['inicio']+2}) → …",ha='center',fontsize=13)
    ax.text(4.5,.45,'Ilustração conceitual. Uma sequência finita não prova a proposição universal.',ha='center',fontsize=9,color='#5c6a63')
    b=BytesIO();fig.tight_layout();fig.savefig(b,format='png',facecolor='white');plt.close(fig)
    raw=b.getvalue()
    if len(raw)>2_000_000:raise ValueError('Ilustração acima do limite.')
    return {'familia':'ilustracao','dados':s,'verificacao':'nao_verificada','png_disponivel':True,'png':base64.b64encode(raw).decode()}


if __name__=='__main__':
    try:
        raw=sys.stdin.read(2001)
        if len(raw)>2000:raise ValueError('Dados acima do limite.')
        print(json.dumps({'ok':True,'resultado':renderizar(json.loads(raw))},ensure_ascii=False))
    except ValueError as e:print(json.dumps({'ok':False,'erro':str(e)},ensure_ascii=False))
    except Exception:print(json.dumps({'ok':False,'erro':'Ilustração inválida ou indisponível. Confira os rótulos.'},ensure_ascii=False))
