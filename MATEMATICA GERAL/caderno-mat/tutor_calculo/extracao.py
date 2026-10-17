"""Extratores locais: produzem paginas com proveniencia, nunca executam conteudo."""

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import zipfile
import posixpath

from .ooxml import ler_xml, paragrafos_xml

from PIL import Image

MAX_ARQUIVO = 20 * 1024 * 1024
MAX_TEXTO = 1_000_000
MAX_PAGINAS = 500
MAX_OCR = 10
TEXTOS = {'.txt', '.md', '.csv', '.json', '.log', '.tex'}
IMAGENS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'}


@dataclass
class Extracao:
    paginas: list[tuple[int, str]]
    estado: str = 'pronto'
    aviso: str = ''
    metodo: str = 'texto'


def tipo_arquivo(nome):
    ext = Path(nome).suffix.lower()
    if ext == '.pdf': return 'pdf'
    if ext == '.docx': return 'docx'
    if ext == '.pptx': return 'pptx'
    if ext in TEXTOS: return 'texto'
    if ext in IMAGENS: return 'imagem'
    return 'arquivo'


def idiomas_ocr():
    if not shutil.which('tesseract'):
        return []
    try:
        resultado = subprocess.run(['tesseract', '--list-langs'], capture_output=True,
                                   text=True, timeout=5, check=True)
        return [x.strip() for x in resultado.stdout.splitlines()[1:] if x.strip() != 'osd']
    except (OSError, subprocess.SubprocessError):
        return []


def ocr_imagem(imagem):
    idiomas = idiomas_ocr()
    if not idiomas:
        return '', 'OCR indisponivel. Instale Tesseract e o idioma portugues (por).'
    lingua = 'por' if 'por' in idiomas else ('eng' if 'eng' in idiomas else idiomas[0])
    aviso = '' if lingua == 'por' else f'OCR em {lingua}; idioma portugues nao instalado. Revise o texto reconhecido.'
    with tempfile.TemporaryDirectory(prefix='cadernomat-ocr-') as pasta:
        caminho = Path(pasta)/'pagina.png'
        imagem.convert('RGB').save(caminho)
        resultado = subprocess.run(['tesseract', str(caminho), 'stdout', '-l', lingua],
                                   capture_output=True, text=True, timeout=25, check=True)
    return resultado.stdout.strip(), aviso


def imagem_pdf(caminho, pagina=1):
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(str(caminho)) as pdf:
        if pagina < 1 or pagina > len(pdf): raise ValueError('Pagina nao encontrada.')
        folha = pdf[pagina-1]
        try:
            largura, altura = folha.get_size()
            escala = min(2, (12_000_000 / max(1, largura * altura)) ** 0.5)
            bitmap = folha.render(scale=escala)
            try:
                return bitmap.to_pil().copy()
            finally:
                bitmap.close()
        finally:
            folha.close()


def extrair_pdf(caminho):
    from pypdf import PdfReader
    leitor = PdfReader(str(caminho), strict=False)
    if leitor.is_encrypted and not leitor.decrypt(''):
        return Extracao([], 'erro', 'PDF protegido por senha. Envie uma copia sem senha.')
    paginas, avisos = [], []
    limite = min(len(leitor.pages), MAX_PAGINAS)
    if len(leitor.pages) > limite:
        avisos.append(f'Extraidas somente as primeiras {limite} paginas.')
    total, ocr, inicio = 0, 0, time.monotonic()
    for indice in range(limite):
        if time.monotonic() - inicio > 120:
            avisos.append('Tempo de processamento atingido; paginas restantes nao extraidas.')
            break
        texto = leitor.pages[indice].extract_text() or ''
        if not texto.strip():
            if ocr >= MAX_OCR:
                avisos.append(f'Pagina {indice+1} sem texto: limite de {MAX_OCR} paginas de OCR atingido.')
                continue
            ocr += 1
            try:
                texto, aviso = ocr_imagem(imagem_pdf(caminho, indice+1))
                if aviso: avisos.append(f'Pagina {indice+1}: {aviso}')
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
                avisos.append(f'OCR falhou na pagina {indice+1}.')
        if not texto.strip():
            avisos.append(f'Pagina {indice+1} sem texto interpretavel.')
            continue
        restante = MAX_TEXTO - total
        paginas.append((indice+1, texto.strip()[:restante]))
        total += len(paginas[-1][1])
        if total >= MAX_TEXTO:
            avisos.append('Limite de texto extraido atingido.')
            break
    metodo = 'PDF + OCR' if ocr else 'PDF textual'
    return Extracao(paginas, 'parcial' if avisos and paginas else ('pronto' if paginas else 'sem_texto'),
                    ' '.join(dict.fromkeys(avisos))[:4000], metodo)


def validar_office(arquivo):
    itens = arquivo.infolist()
    if len(itens)>2000 or sum(i.file_size for i in itens)>MAX_ARQUIVO:
        raise ValueError('Office expandido excede o limite de 20 MiB.')
    if len({i.filename for i in itens})!=len(itens):
        raise ValueError('Office contém entradas duplicadas.')


def extrair_pptx(caminho):
    p = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
    r = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    avisos = ['PPTX: texto, tabelas e fórmulas OMML básicas; imagens, diagramas, notas e objetos embutidos não interpretados.']
    paginas, total = [], 0
    with zipfile.ZipFile(caminho) as doc:
        validar_office(doc)
        raiz = ler_xml(doc,'ppt/presentation.xml')
        relacoes = {e.get('Id'):e for e in ler_xml(doc,'ppt/_rels/presentation.xml.rels')}
        slides = raiz.findall(p+'sldIdLst/'+p+'sldId')
        if len(slides)>MAX_PAGINAS: avisos.append(f'Extraídos somente os primeiros {MAX_PAGINAS} slides.')
        for numero, slide in enumerate(slides[:MAX_PAGINAS],1):
            rel = relacoes[slide.get(r+'id')]
            if rel.get('TargetMode')=='External': raise ValueError('Slide externo não suportado.')
            destino = rel.get('Target','')
            nome = posixpath.normpath(destino.lstrip('/') if destino.startswith('/') else 'ppt/'+destino)
            if not nome.startswith('ppt/slides/') or not nome.endswith('.xml'):
                raise ValueError('Destino de slide inválido.')
            texto, alertas = paragrafos_xml(ler_xml(doc,nome))
            avisos.extend(f'Slide {numero}: {a}' for a in alertas)
            if texto:
                paginas.append((numero,texto[:MAX_TEXTO-total])); total += len(paginas[-1][1])
            else: avisos.append(f'Slide {numero} sem texto interpretável; consulte o original.')
            if total>=MAX_TEXTO:
                avisos.append('Limite de texto extraído atingido.'); break
    return Extracao(paginas,'parcial' if paginas else 'sem_texto',' '.join(dict.fromkeys(avisos))[:4000], 'PPTX + OMML básico')


def extrair(caminho, nome):
    caminho = Path(caminho)
    tipo = tipo_arquivo(nome)
    try:
        if tipo == 'pdf':
            return extrair_pdf(caminho)
        if tipo == 'pptx':
            return extrair_pptx(caminho)
        if tipo == 'imagem':
            with Image.open(caminho) as img:
                if img.width * img.height > 40_000_000:
                    return Extracao([], 'erro', 'Imagem excede 40 milhoes de pixels.')
                img.load()
                texto, aviso = ocr_imagem(img)
                if getattr(img, 'n_frames', 1)>1:
                    aviso += ' Apenas o primeiro quadro da imagem foi interpretado.'
            return Extracao([(1, texto[:MAX_TEXTO])] if texto else [],
                            'parcial' if aviso and texto else ('pronto' if texto else 'sem_texto'),
                            aviso or ('' if texto else 'OCR nao encontrou texto legivel.'), 'OCR')
        if tipo == 'texto':
            bruto = caminho.read_bytes()
            if b'\x00' in bruto:
                return Extracao([], 'erro', 'Arquivo binario ou codificacao nao suportada. Use UTF-8.')
            try:
                texto = bruto.decode('utf-8-sig')
                aviso = ''
            except UnicodeDecodeError:
                texto = bruto.decode('cp1252')
                aviso = 'Texto lido como Windows-1252; prefira UTF-8.'
        elif tipo == 'docx':
            with zipfile.ZipFile(caminho) as doc:
                validar_office(doc)
                texto, alertas = paragrafos_xml(ler_xml(doc,'word/document.xml'))
            aviso = 'DOCX: texto, tabelas e fórmulas OMML básicas; sem paginação, figuras ou objetos embutidos. '+' '.join(alertas)
        else:
            return Extracao([], 'nao_suportado', 'Formato armazenado, mas nao interpretado pela IA. Envie PDF, imagem, DOCX, PPTX ou texto.')
        if len(texto) > MAX_TEXTO:
            aviso += ' Texto truncado no limite de 1 milhao de caracteres.'
        if not texto.strip():
            return Extracao([], 'sem_texto', 'Documento vazio ou sem texto interpretavel.')
        return Extracao([(1, texto.strip()[:MAX_TEXTO])], 'parcial' if aviso else 'pronto', aviso, tipo)
    except Exception:
        # Nao exibir conteudo binario, caminhos sensiveis ou resposta bruta de servidores.
        return Extracao([], 'erro', 'Nao foi possivel interpretar o arquivo. Confira o formato e tente reprocessar.')


class TextoHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes, self.ignorar = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'noscript', 'template', 'svg'}: self.ignorar += 1
        if not self.ignorar and tag in {'p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'tr'}: self.partes.append('\n')

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript', 'template', 'svg'} and self.ignorar:
            self.ignorar -= 1
        if not self.ignorar and tag in {'p', 'div', 'li', 'tr'}: self.partes.append('\n')

    def handle_data(self, data):
        if not self.ignorar: self.partes.append(data)

    def texto(self):
        return '\n'.join(' '.join(linha.split()) for linha in ''.join(self.partes).splitlines() if linha.strip())
