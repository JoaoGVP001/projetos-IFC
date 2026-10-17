"""Operações finitas e parser proposicional limitado, sem eval, rede ou banco."""
import base64
import io
import itertools
import json
import math
import re
import sys

VERSAO = 'discreta-v1'
MAX_ELEMENTOS = 40
MAX_PARES = 400
MAX_ENTRADA = 6000
MAX_VARIAVEIS = 6
CAMPOS = ('A','B','U','R','S','C','expressao','comparar')


def ordem(x): return (0,x) if type(x) is int else (1,x)
def ordenar(xs): return sorted(xs,key=ordem)
def mostrar(x): return str(x) if type(x) is int else json.dumps(x,ensure_ascii=False)
def conjunto(xs): return '{'+', '.join(mostrar(x) for x in ordenar(xs))+'}'
def pares(xs): return '{'+', '.join('('+mostrar(a)+', '+mostrar(b)+')' for a,b in sorted(xs,key=lambda p:(ordem(p[0]),ordem(p[1]))))+'}'


def elemento(x):
    if type(x) is int and abs(x)<=1_000_000:return x
    if isinstance(x,str) and re.fullmatch(r'[^\W\d]\w{0,19}',x,re.UNICODE) and x[0].isalpha():return x
    raise ValueError('Elementos: inteiros de -1000000 a 1000000 ou nomes de até 20 letras/dígitos, começando por letra.')


TOKEN = re.compile(r'\s*("(?:[^"\\]|\\.)*"|[+-]?\d+|[^\W\d]\w*|[{},()])',re.UNICODE)
def ler(texto, relacao=False):
    if not isinstance(texto,str) or len(texto)>MAX_ENTRADA:raise ValueError('Entrada acima do limite de 6000 caracteres.')
    texto=texto.strip()
    if texto=='∅':texto='{}'
    if not texto.startswith('{') or not texto.endswith('}'):
        raise ValueError('Use conjuntos finitos entre chaves, por exemplo {1, 2, "a"}. Intervalos e conjuntos infinitos estão fora do escopo.')
    tokens=[];pos=0
    while pos<len(texto):
        m=TOKEN.match(texto,pos)
        if not m:raise ValueError('Notação inválida. Use elementos separados por vírgula e pares (a,b).')
        tokens.append(m[1]);pos=m.end()
        if len(tokens)>2500:raise ValueError('Entrada tem tokens demais.')
    index=1;out=[]
    def take(expected=None):
        nonlocal index
        if index>=len(tokens):raise ValueError('Entrada incompleta.')
        t=tokens[index];index+=1
        if expected is not None and t!=expected:raise ValueError('Esperado '+expected+'.')
        return t
    def atom():
        t=take()
        if t.startswith('"'):
            try:x=json.loads(t)
            except ValueError:raise ValueError('Nome entre aspas inválido.') from None
        elif re.fullmatch(r'[+-]?\d+',t):
            if len(t)>8:raise ValueError('Inteiro acima do limite.')
            x=int(t)
        else:x=t
        return elemento(x)
    if tokens[index]!='}':
        while True:
            if relacao:
                take('(');a=atom();take(',');b=atom();take(')');out.append((a,b))
            else:out.append(atom())
            if len(out)>(MAX_PARES if relacao else MAX_ELEMENTOS):raise ValueError('Limite: 40 elementos ou 400 pares por entrada.')
            if index>=len(tokens):raise ValueError('Entrada incompleta.')
            if tokens[index]=='}':break
            take(',')
    take('}')
    if index!=len(tokens):raise ValueError('Dados depois do conjunto não são aceitos.')
    return set(out)


class Logica:
    def __init__(self,texto):
        if not isinstance(texto,str) or not texto.strip() or len(texto)>300:raise ValueError('Expressão lógica: 1 a 300 caracteres.')
        rx=re.compile(r'\s*(<->|->|[¬~!∧&∨|→↔()]|[a-zA-Z])')
        self.tokens=[];pos=0
        while pos<len(texto.rstrip()):
            m=rx.match(texto,pos)
            if not m:raise ValueError('Lógica: use letras, ¬/~, ∧/&, ∨/|, →/->, ↔/<-> e parênteses.')
            t={'~':'¬','!':'¬','&':'∧','|':'∨','->':'→','<->':'↔'}.get(m[1],m[1]);self.tokens.append(t);pos=m.end()
            if len(self.tokens)>150:raise ValueError('Expressão excede 150 tokens.')
        self.i=0;self.raiz=self.parse(0,0)
        if self.i!=len(self.tokens):raise ValueError('Expressão incompleta ou parênteses incorretos.')
        stack=[(self.raiz,0)]
        while stack:
            node,depth=stack.pop()
            if depth>20:raise ValueError('Expressão excede 20 níveis.')
            stack.extend((child,depth+1) for child in node[1:] if isinstance(child,tuple))
        self.variaveis=sorted(set(t for t in self.tokens if t.isascii() and t.isalpha()))
        if len(self.variaveis)>MAX_VARIAVEIS:raise ValueError('Use até seis variáveis proposicionais.')
    def parse(self,minimo,depth):
        if depth>20:raise ValueError('Expressão excede 20 níveis.')
        if self.i>=len(self.tokens):raise ValueError('Operando ausente.')
        t=self.tokens[self.i];self.i+=1
        if t=='¬':left=('¬',self.parse(5,depth+1))
        elif t=='(':
            left=self.parse(0,depth+1)
            if self.i>=len(self.tokens) or self.tokens[self.i]!=')':raise ValueError('Feche os parênteses.')
            self.i+=1
        elif t.isascii() and t.isalpha():left=('var',t)
        else:raise ValueError('Esperado uma variável ou negação.')
        precedence={'↔':1,'→':2,'∨':3,'∧':4}
        while self.i<len(self.tokens) and (op:=self.tokens[self.i]) in precedence and precedence[op]>=minimo:
            self.i+=1;right=self.parse(precedence[op] if op=='→' else precedence[op]+1,depth+1);left=(op,left,right)
        return left
    def normalizada(self,node=None):
        node=self.raiz if node is None else node
        if node[0]=='var':return node[1]
        if node[0]=='¬':return '¬'+self.normalizada(node[1])
        return '('+self.normalizada(node[1])+' '+node[0]+' '+self.normalizada(node[2])+')'
    def avaliar(self,valores,node=None):
        node=self.raiz if node is None else node;op=node[0]
        if op=='var':return valores[node[1]]
        a=self.avaliar(valores,node[1])
        if op=='¬':return not a
        b=self.avaliar(valores,node[2])
        return {'∧':a and b,'∨':a or b,'→':(not a) or b,'↔':a==b}[op]


def validar_spec(d,incompleta=False,verificar_campos=True):
    if not isinstance(d,dict) or set(d)-{'tipo','sobre',*CAMPOS}:raise ValueError('Parâmetros discretos desconhecidos.')
    if d.get('tipo') not in ('conjuntos','relacoes','logica'):raise ValueError('Escolha conjuntos, relações ou lógica.')
    if type(d.get('sobre',True)) is not bool:raise ValueError('Escolha se a relação está sobre A.')
    out={'tipo':d['tipo'],'sobre':d.get('sobre',True)}
    for k in CAMPOS:
        v=d.get(k,'')
        if incompleta and v is None:v=''
        if not isinstance(v,str) or len(v)>(300 if k in ('expressao','comparar') else MAX_ENTRADA) or '\x00' in v:raise ValueError('Campo inválido ou acima do limite.')
        out[k]=v.strip()
    required={'conjuntos':['A','B'],'relacoes':['A','R']+([] if out['sobre'] else ['B']),'logica':['expressao']}[out['tipo']]
    if out['tipo']=='relacoes' and out['S'] and not out['sobre']:required.append('C')
    if not incompleta and any(not out[k] for k in required):raise ValueError('Preencha: '+', '.join(required)+'. Use {} para um conjunto vazio.')
    active={'conjuntos':('A','B','U'),'relacoes':('A','B','C','R','S'),'logica':('expressao','comparar')}[out['tipo']]
    for k in CAMPOS:
        if k not in active:out[k]=''
        elif out[k] and verificar_campos:Logica(out[k]) if k in ('expressao','comparar') else ler(out[k],k in ('R','S'))
    if out['tipo']=='relacoes' and out['sobre']:out['B']='';out['C']=''
    if not incompleta:interpretar(out)
    return out


def interpretar(spec):
    if spec['tipo']=='logica':
        a=Logica(spec['expressao']);b=Logica(spec['comparar']) if spec['comparar'] else None
        if len(set(a.variaveis+(b.variaveis if b else [])))>6:raise ValueError('As duas expressões juntas devem ter até seis variáveis.')
        return {'expressao':a.normalizada(),'comparar':b.normalizada() if b else '', 'precedencia':'¬ > ∧ > ∨ > → > ↔; → associa à direita, demais operadores binários à esquerda.'}
    a=ler(spec['A']);b=a if spec['tipo']=='relacoes' and spec['sobre'] else ler(spec['B'])
    dados={'A':ordenar(a),'B':ordenar(b)}
    if spec['tipo']=='conjuntos':
        if spec['U']:
            u=ler(spec['U'])
            if not (a|b)<=u:raise ValueError('A e B precisam estar contidos no universo U.')
            dados['U']=ordenar(u)
    else:
        r=ler(spec['R'],True)
        if any(x not in a or y not in b for x,y in r):raise ValueError('Há pares de R fora de A × B.')
        dados['R']=[list(p) for p in sorted(r,key=lambda p:(ordem(p[0]),ordem(p[1])))];dados['sobre']=spec['sobre']
        if spec['S']:
            c=a if spec['sobre'] else ler(spec['C']);s=ler(spec['S'],True)
            if any(x not in b or y not in c for x,y in s):raise ValueError('S deve estar contida em B × C; a composição é S ∘ R.')
            dados['C']=ordenar(c);dados['S']=[list(p) for p in sorted(s,key=lambda p:(ordem(p[0]),ordem(p[1])))]
    return dados


DEFINICOES={
'reflexiva':'Para todo a em A, (a,a) pertence a R.',
'irreflexiva':'Para todo a em A, (a,a) não pertence a R.',
'simetrica':'Se (a,b) pertence a R, então (b,a) também pertence.',
'antissimetrica':'Se (a,b) e (b,a) pertencem a R, então a=b.',
'transitiva':'Se (a,b) e (b,c) pertencem a R, então (a,c) também pertence.'}

def propriedades(a,r):
    pairs=sorted(r,key=lambda p:(ordem(p[0]),ordem(p[1])))
    witnesses={
      'reflexiva':next(([x,x] for x in ordenar(a) if (x,x) not in r),None),
      'irreflexiva':next(([x,x] for x in ordenar(a) if (x,x) in r),None),
      'simetrica':next(([x,y] for x,y in pairs if (y,x) not in r),None),
      'antissimetrica':next(([x,y] for x,y in pairs if x!=y and (y,x) in r),None),
      'transitiva':next(([x,y,z] for x,y in pairs for yy,z in pairs if y==yy and (x,z) not in r),None)}
    return [{'propriedade':k,'definicao':DEFINICOES[k],'vale':v is None,'contraexemplo':v,
      'justificativa':('Todos os casos do conjunto finito declarado foram conferidos.' if a else 'Vale por vacuidade: A é vazio.') if v is None else
      {'reflexiva':'Falta o par diagonal indicado.','irreflexiva':'O par diagonal indicado está presente.',
       'simetrica':'O par está presente, mas seu inverso está ausente.','antissimetrica':'Os dois sentidos existem entre elementos distintos.',
       'transitiva':'Os dois primeiros pares existem, mas o par entre o primeiro e o terceiro elemento está ausente.'}[k]} for k,v in witnesses.items()]


def diagrama(dados,tipo):
    if any(isinstance(x,str) and len(x)>10 for x in dados['A']+dados['B']) or len(dados['A'])+len(dados['B'])>20 or (tipo=='relacoes' and len(dados['R'])>30):return None,'Diagrama omitido: limite visual de 20 elementos somados, rótulos de até 10 caracteres e 30 pares. Os resultados textuais continuam completos.'
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.patches import Circle,FancyArrowPatch,FancyBboxPatch
    fig=Figure(figsize=(8,5),dpi=120,facecolor='#f5f7f3');FigureCanvasAgg(fig);ax=fig.add_subplot(111);ax.axis('off')
    if tipo=='conjuntos':
        a=set(dados['A']);b=set(dados['B'])
        for cx,label in ((-.6,'A'),(.6,'B')):
            ax.add_patch(Circle((cx,0),1,color='#dceae2',alpha=.5));ax.add_patch(Circle((cx,0),1,fill=False,ec='#13766c',lw=2));ax.text(cx,1.15,label,ha='center',weight='bold')
        for x,xs in ((-1.1,a-b),(0,a&b),(1.1,b-a)):ax.text(x,0,'\n'.join(mostrar(e) for e in ordenar(xs)) or '∅',ha='center',va='center',fontsize=10)
        ax.set(xlim=(-2,2),ylim=(-1.5,1.5),aspect='equal');ax.set_title('A − B          A ∩ B          B − A')
    else:
        a=dados['A'];b=dados['B'];r=dados['R'];sobre=dados['sobre']
        if sobre:
            coords={('A',v):(math.cos(2*math.pi*i/max(1,len(a))),math.sin(2*math.pi*i/max(1,len(a)))) for i,v in enumerate(a)}
        else:
            coords={**{('A',v):(-1,1-2*i/max(1,len(a)-1)) for i,v in enumerate(a)},**{('B',v):(1,1-2*i/max(1,len(b)-1)) for i,v in enumerate(b)}}
            ax.text(-1,1.5,'Origem A',ha='center');ax.text(1,1.5,'Destino B',ha='center')
        crowded=not sobre and max(len(a),len(b))>7
        nodes={}
        for key,(x,y) in coords.items():
            label=mostrar(key[1]);height=.18 if crowded else .30
            if len(label)<=3:node=Circle((x,y),height/2)
            else:node=FancyBboxPatch((x-(.072*len(label)+.14)/2,y-height/2),.072*len(label)+.14,height,boxstyle='round,pad=0.01,rounding_size=0.07')
            node.set(facecolor='#f5f7f3',edgecolor='#13766c',zorder=3);ax.add_patch(node);nodes[key]=node
            ax.text(x,y,label,ha='center',va='center',fontsize=8 if crowded else 9,zorder=4)
        for x,y in r:
            start=coords['A',x];end=coords['A' if sobre else 'B',y]
            if sobre and x==y:
                sx,sy=start;long=len(mostrar(x))>3;offset=.18 if long else .07
                patch=FancyArrowPatch((sx-.09,sy+offset),(sx+.09,sy+offset),connectionstyle='arc3,rad=-2.5',patchA=None if long else nodes['A',x],patchB=None if long else nodes['A',x],shrinkA=2,shrinkB=2,arrowstyle='-|>',mutation_scale=12,color='#956323')
            else:patch=FancyArrowPatch(start,end,patchA=nodes['A',x],patchB=nodes['A' if sobre else 'B',y],connectionstyle='arc3,rad='+('0.17' if sobre else '0'),arrowstyle='-|>',mutation_scale=12,shrinkA=4,shrinkB=4,color='#13766c')
            ax.add_patch(patch)
        if not coords:ax.text(0,0,'Conjunto vazio; nenhuma seta.',ha='center')
        ax.set(xlim=(-1.7,1.7),ylim=(-1.7,1.7),aspect='equal');ax.set_title('Relação R sobre A' if sobre else 'R ⊆ A × B')
    buf=io.BytesIO();fig.savefig(buf,format='png',dpi=120);raw=buf.getvalue()
    if len(raw)>2_000_000:raise ValueError('Diagrama excede 2 MB.')
    return base64.b64encode(raw).decode(),''


def calcular(spec):
    spec=validar_spec(spec);d=interpretar(spec)
    out={'familia':'discreta','versao':VERSAO,'tipo':spec['tipo'],'dados':d,'resultados':{},'avisos':['Verificação exata sobre os dados finitos apresentados; não certifica interpretação do enunciado, explicações ou provas por indução.'],'png':None}
    r=out['resultados']
    if spec['tipo']=='conjuntos':
        a=set(d['A']);b=set(d['B'])
        r.update(uniao=ordenar(a|b),intersecao=ordenar(a&b),diferenca_A_B=ordenar(a-b),diferenca_B_A=ordenar(b-a),diferenca_simetrica=ordenar(a^b),produto_cartesiano=[list(p) for p in itertools.product(ordenar(a),ordenar(b))],cardinalidade_A=len(a),cardinalidade_B=len(b),iguais=a==b,A_contido_B=a<=b,B_contido_A=b<=a)
        if 'U' in d:r.update(complemento_A=ordenar(set(d['U'])-a),complemento_B=ordenar(set(d['U'])-b))
        else:out['avisos'].append('Complementos não calculados: informe explicitamente o universo U.')
    elif spec['tipo']=='relacoes':
        a=set(d['A']);rr={tuple(p) for p in d['R']}
        r.update(dominio=ordenar({x for x,y in rr}),imagem=ordenar({y for x,y in rr}),inversa=[list(p) for p in sorted(((y,x) for x,y in rr),key=lambda p:(ordem(p[0]),ordem(p[1])))],propriedades=propriedades(a,rr) if spec['sobre'] else [])
        if not spec['sobre']:out['avisos'].append('As cinco propriedades são verificadas somente no modo relação sobre A.')
        if 'S' in d:r['composicao_S_R']=[list(p) for p in sorted({(x,z) for x,y in rr for yy,z in d['S'] if y==yy},key=lambda p:(ordem(p[0]),ordem(p[1])))];out['avisos'].append('S ∘ R: primeiro R, depois S, passando pelo conjunto intermediário B.')
    else:
        a=Logica(spec['expressao']);b=Logica(spec['comparar']) if spec['comparar'] else None
        variables=sorted(set(a.variaveis+(b.variaveis if b else [])));rows=[]
        for vals in itertools.product((True,False),repeat=len(variables)):
            v=dict(zip(variables,vals));row={'valores':v,'resultado':a.avaliar(v)}
            if b:row['comparacao']=b.avaliar(v)
            rows.append(row)
        r.update(variaveis=variables,linhas=rows,classificacao='tautologia' if all(x['resultado'] for x in rows) else 'contradição' if not any(x['resultado'] for x in rows) else 'contingência')
        if b:
            witness=next((x['valores'] for x in rows if x['resultado']!=x['comparacao']),None);r.update(equivalentes=witness is None,contraexemplo=witness)
    if spec['tipo']!='logica':out['png'],aviso=diagrama(d,spec['tipo']);out['avisos'].extend([aviso] if aviso else [])
    return out


def resumo(r):
    lines=['### Matemática Discreta · cálculo local','**Verificado nos dados informados** · '+r['versao'],'Dados interpretados:']
    for k,v in r['dados'].items():
        if k=='sobre':continue
        lines.append(k+': '+(pares(v) if k in ('R','S') else conjunto(v) if isinstance(v,list) else str(v)))
    nomes={'uniao':'União','intersecao':'Interseção','diferenca_A_B':'A − B','diferenca_B_A':'B − A','diferenca_simetrica':'Diferença simétrica','produto_cartesiano':'A × B','cardinalidade_A':'Cardinalidade de A','cardinalidade_B':'Cardinalidade de B','iguais':'A = B','A_contido_B':'A ⊆ B','B_contido_A':'B ⊆ A','complemento_A':'U − A','complemento_B':'U − B','dominio':'Domínio','imagem':'Imagem','inversa':'Relação inversa','composicao_S_R':'Composição S ∘ R','variaveis':'Variáveis','classificacao':'Classificação','equivalentes':'Expressões equivalentes','contraexemplo':'Atribuição que demonstra diferença'}
    for k,v in r['resultados'].items():
        if k=='linhas':
            variables=r['resultados']['variaveis'];headers=variables+['Resultado']+(['Comparação'] if r['dados'].get('comparar') else [])
            lines.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join('V' if x else 'F' for x in [*[row['valores'][key] for key in variables],row['resultado']]+([row['comparacao']] if 'comparacao' in row else []))+' |' for row in v))
        elif k=='propriedades':
            for p in v:lines.append('**'+p['propriedade']+' · '+('Vale' if p['vale'] else 'Não vale')+'**\n'+p['definicao']+'\n'+p['justificativa']+('\nContraexemplo: '+json.dumps(p['contraexemplo'],ensure_ascii=False) if p['contraexemplo'] else ''))
        else:lines.append('**'+nomes.get(k,k)+'**: '+('Sim' if v is True else 'Não' if v is False else 'Nenhum' if v is None else v if isinstance(v,str) else json.dumps(v,ensure_ascii=False)))
    lines.extend(r['avisos']);return '\n\n'.join(lines)


def parametros_explicitos(raw,texto,fontes=""):
    """Uma proposta nunca preenche conjuntos/pares inventados pelo modelo."""
    texto=texto.replace("$","");fontes=fontes.replace("$","")
    # Valide tipos/limites do contrato antes de descartar notações inventadas.
    out=validar_spec(raw,incompleta=True,verificar_campos=False)
    for k in CAMPOS:
        pattern=r'\b'+k+r'\s*[=:]\s*(\{[^{}]*\}|∅)' if k not in ('expressao','comparar') else r'\b'+k+r'\s*[=:]\s*([^;\n]+)'
        values=list(dict.fromkeys(m[1].strip() for m in re.finditer(pattern,texto,re.I)))
        if not values:values=list(dict.fromkeys(m[1].strip() for m in re.finditer(pattern,fontes,re.I)))
        out[k]=values[0] if len(values)==1 else ''
    if out['tipo']=='relacoes':out['sobre']=not bool(out['B'])
    return validar_spec(out,incompleta=True)


def main():
    try:
        if sys.platform=='linux':
            import resource
            resource.setrlimit(resource.RLIMIT_AS,(1_500_000_000,1_500_000_000));resource.setrlimit(resource.RLIMIT_CPU,(22,23))
        raw=sys.stdin.read(55000)
        if len(raw)>54000:raise ValueError('Pedido acima do limite.')
        d=json.loads(raw)
        if set(d)=={'validar'}:result=interpretar(validar_spec(d['validar']))
        elif set(d) in ({'proposta','texto'},{'proposta','texto','fontes'}):result=parametros_explicitos(d['proposta'],d['texto'],d.get('fontes',''))
        else:result=calcular(d)
        print(json.dumps({'ok':True,'resultado':result},ensure_ascii=False,allow_nan=False))
    except Exception as e:print(json.dumps({'ok':False,'erro':str(e) if isinstance(e,ValueError) else 'Falha na operação discreta; resultado não verificado.'},ensure_ascii=False))

if __name__=='__main__':main()
