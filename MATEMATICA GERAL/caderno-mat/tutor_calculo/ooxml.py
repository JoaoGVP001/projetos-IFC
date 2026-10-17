"""Leitura limitada de XML do Office e fórmulas OMML, sem executar conteúdo."""
import re
import unicodedata
import xml.etree.ElementTree as ET

M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'


def ler_xml(arquivo, nome):
    bruto = arquivo.read(nome)
    if re.search(br'<!\s*(?:DOCTYPE|ENTITY)\b', bruto.replace(b'\x00',b''), re.I):
        raise ValueError('Declarações de entidades não são suportadas.')
    return ET.fromstring(bruto)


def filhos(elemento):
    # O mesmo texto pode existir como Choice e Fallback. Leia uma representação.
    if elemento.tag == MC+'AlternateContent':
        escolha = elemento.find(MC+'Choice')
        if escolha is None: escolha = elemento.find(MC+'Fallback')
        return list(escolha) if escolha is not None else []
    return list(elemento)


def formula(elemento, profundidade=0):
    if profundidade > 40: raise ValueError('Fórmula muito profunda.')
    tag = elemento.tag.removeprefix(M)
    def converter(e): return formula(e, profundidade+1)
    def parte(nome):
        filho = elemento.find(M+nome)
        if filho is None: raise ValueError('Fórmula incompleta.')
        return converter(filho)
    if tag == 't':
        texto = unicodedata.normalize('NFKC', elemento.text or '')
        especiais = {'\\': r'\backslash ', '{': r'\{', '}': r'\}', '_': r'\_',
                     '$': r'\$', '%': r'\%', '#': r'\#', '&': r'\&'}
        return ''.join(especiais.get(c,c) for c in texto)
    if tag.endswith('Pr') or tag in {'ctrlPr'}: return ''
    if tag in {'oMath', 'oMathPara', 'r', 'e', 'num', 'den', 'sup', 'sub', 'deg'}:
        return ''.join(converter(e) for e in filhos(elemento) if e.tag.startswith(M))
    if tag == 'f':
        tipo = elemento.find(M+'fPr/'+M+'type')
        comando = 'binom' if tipo is not None and tipo.get(M+'val')=='noBar' else 'frac'
        return '\\'+comando+'{'+parte('num')+'}{'+parte('den')+'}'
    if tag == 'sSup': return '{'+parte('e')+'}^{'+parte('sup')+'}'
    if tag == 'sSub': return '{'+parte('e')+'}_{'+parte('sub')+'}'
    if tag == 'sSubSup': return '{'+parte('e')+'}_{'+parte('sub')+'}^{'+parte('sup')+'}'
    if tag == 'rad':
        grau = parte('deg')
        return r'\sqrt'+('['+grau+']' if grau else '')+'{'+parte('e')+'}'
    if tag == 'd':
        def delimitador(nome, padrao):
            prop = elemento.find(M+'dPr/'+M+nome)
            valor = prop.get(M+'val',padrao) if prop is not None else padrao
            if valor not in ('', '(', ')', '[', ']', '{', '}', '|', '‖', '⟨', '⟩'):
                raise ValueError('Delimitador não suportado.')
            return {'':'.','{':r'\{','}':r'\}','‖':r'\Vert','⟨':r'\langle','⟩':r'\rangle'}.get(valor,valor)
        partes = [converter(e) for e in elemento.findall(M+'e')]
        if not partes: raise ValueError('Fórmula incompleta.')
        separador = elemento.find(M+'dPr/'+M+'sepChr')
        sep = separador.get(M+'val','|') if separador is not None else '|'
        if len(sep)>1: raise ValueError('Separador não suportado.')
        return r'\left'+delimitador('begChr','(')+sep.join(partes)+r'\right'+delimitador('endChr',')')
    raise ValueError('Estrutura matemática não suportada.')


def paragrafos_xml(raiz):
    """Parágrafos/tabelas e fórmulas básicas; conserva avisos de dados ausentes."""
    avisos = set()
    def alinhamento(e):
        if e.tag == W+'r':
            prop = e.find(W+'rPr/'+W+'vertAlign')
            return prop.get(W+'val') if prop is not None else None
        if e.tag == A+'r':
            prop = e.find(A+'rPr')
            baseline = int(prop.get('baseline','0')) if prop is not None else 0
            return 'superscript' if baseline>0 else 'subscript' if baseline<0 else None
        return None
    def sequencia(e, profundidade):
        if profundidade>80: raise ValueError('XML muito profundo.')
        itens, partes, indice = filhos(e), [], 0
        while indice<len(itens):
            filho = itens[indice]; classe = alinhamento(filho)
            if classe in ('superscript','subscript'):
                valores = []
                while indice<len(itens) and alinhamento(itens[indice])==classe:
                    valores.append(sequencia(itens[indice],profundidade+1)); indice += 1
                valor = ''.join(valores).strip()
                if valor: partes.append(('^' if classe=='superscript' else '_')+'{'+valor+'}')
            else:
                partes.append(texto(filho,profundidade+1)); indice += 1
        return ''.join(partes)
    def texto(e, profundidade=0):
        if profundidade > 80: raise ValueError('XML muito profundo.')
        if e.tag in (A+'t', W+'t'): return e.text or ''
        if e.tag in (A+'br', W+'br'): return '\n'
        if e.tag == W+'tab': return '\t'
        if e.tag in (W+'r', A+'r'):
            valor = sequencia(e, profundidade).strip() if alinhamento(e) else sequencia(e,profundidade)
            classe = alinhamento(e)
            if classe in ('superscript','subscript') and valor:
                return ('^' if classe=='superscript' else '_')+'{'+valor+'}'
            return valor
        if e.tag == M+'oMath':
            try: return ' $'+formula(e)+'$ '
            except ValueError:
                avisos.add('Equações não suportadas foram sinalizadas; consulte o original.')
                return ' [Equação não interpretada: consulte o original.] '
        return sequencia(e, profundidade)
    def percorrer(e, profundidade=0):
        if profundidade > 80: raise ValueError('XML muito profundo.')
        if e.tag in (A+'p', W+'p'):
            valor = texto(e).strip()
            # Revisões ortográficas podem separar o mesmo expoente em vários runs.
            for _ in range(40):
                novo = re.sub(r'([\^_])\{([^{}]*)\}\1\{([^{}]*)\}',r'\1{\2\3}',valor)
                if novo==valor: break
                valor = novo
            if valor and e.find(W+'pPr/'+W+'numPr') is not None: valor = '• '+valor
            if valor: yield valor
            return
        for c in filhos(e): yield from percorrer(c, profundidade+1)
    linhas = list(percorrer(raiz))
    return '\n'.join(linhas), sorted(avisos)
