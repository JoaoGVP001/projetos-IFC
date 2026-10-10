from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import posixpath
import re
import tempfile
from typing import Any
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from validacoes import FORMATOS_IMAGEM, validar_arquivo


def _chave_natural(nome: str) -> list[int | str]:
    return [int(parte) if parte.isdigit() else parte.casefold() for parte in re.split(r"(\d+)", nome)]


def _nomes_imagens(nomes: list[str]) -> list[str]:
    paginas = [nome for nome in nomes if Path(nome).suffix.lower() in FORMATOS_IMAGEM]
    return sorted(paginas, key=_chave_natural)


class LeitorArquivo(ABC):
    def __init__(self, caminho: str | Path) -> None:
        self.caminho = validar_arquivo(caminho)
        self._aberto = False

    @abstractmethod
    def abrir(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def obter_pagina(self, numero: int) -> Any:
        raise NotImplementedError

    @property
    @abstractmethod
    def total_paginas(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def fechar(self) -> None:
        raise NotImplementedError

    def _validar_numero_pagina(self, numero: int) -> None:
        if numero < 0 or numero >= self.total_paginas:
            raise ValueError("Página fora dos limites da obra.")


class LeitorPDF(LeitorArquivo):
    def __init__(self, caminho: str | Path) -> None:
        super().__init__(caminho)
        self._documento: Any = None

    def abrir(self) -> None:
        try:
            import fitz

            self._documento = fitz.open(self.caminho)
            if self._documento.page_count == 0:
                raise ValueError("O PDF não possui páginas.")
            self._aberto = True
        except ImportError as erro:
            raise RuntimeError("Instale a dependência PyMuPDF para ler arquivos PDF.") from erro
        except Exception as erro:
            raise ValueError(f"Não foi possível abrir o PDF: {erro}") from erro

    @property
    def total_paginas(self) -> int:
        return self._documento.page_count if self._documento else 0

    def obter_pagina(self, numero: int) -> Any:
        if not self._aberto:
            self.abrir()
        self._validar_numero_pagina(numero)
        try:
            from PIL import Image

            pagina = self._documento.load_page(numero)
            pixmap = pagina.get_pixmap(matrix=self._matriz_renderizacao(), alpha=False)
            return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        except ImportError as erro:
            raise RuntimeError("Instale a dependência Pillow para exibir páginas.") from erro

    @staticmethod
    def _matriz_renderizacao() -> Any:
        import fitz

        return fitz.Matrix(1.6, 1.6)

    def fechar(self) -> None:
        if self._documento:
            self._documento.close()
        self._documento = None
        self._aberto = False


class LeitorCBZ(LeitorArquivo):
    def __init__(self, caminho: str | Path) -> None:
        super().__init__(caminho)
        self._arquivo: ZipFile | None = None
        self._paginas: list[str] = []

    def abrir(self) -> None:
        try:
            self._arquivo = ZipFile(self.caminho)
            self._paginas = _nomes_imagens(self._arquivo.namelist())
            if not self._paginas:
                raise ValueError("O arquivo CBZ não contém imagens.")
            self._aberto = True
        except (BadZipFile, OSError) as erro:
            raise ValueError(f"Não foi possível abrir o CBZ: {erro}") from erro

    @property
    def total_paginas(self) -> int:
        return len(self._paginas)

    def obter_pagina(self, numero: int) -> Any:
        if not self._aberto:
            self.abrir()
        self._validar_numero_pagina(numero)
        from PIL import Image

        if self._arquivo is None:
            raise RuntimeError("O arquivo CBZ não está aberto.")
        with self._arquivo.open(self._paginas[numero]) as pagina:
            imagem = Image.open(BytesIO(pagina.read()))
            imagem.load()
            return imagem.convert("RGB")

    def fechar(self) -> None:
        if self._arquivo:
            self._arquivo.close()
        self._arquivo = None
        self._paginas = []
        self._aberto = False


class LeitorCBR(LeitorArquivo):
    def __init__(self, caminho: str | Path) -> None:
        super().__init__(caminho)
        self._arquivo: Any = None
        self._paginas: list[str] = []

    def abrir(self) -> None:
        try:
            import rarfile

            self._arquivo = rarfile.RarFile(self.caminho)
            self._paginas = _nomes_imagens(self._arquivo.namelist())
            if not self._paginas:
                raise ValueError("O arquivo CBR não contém imagens.")
            self._aberto = True
        except ImportError as erro:
            raise RuntimeError("Instale a dependência rarfile para ler arquivos CBR.") from erro
        except Exception as erro:
            raise ValueError(
                "Não foi possível abrir o CBR. Verifique se o arquivo é válido e se "
                f"UnRAR, 7-Zip ou bsdtar está instalado. Detalhes: {erro}"
            ) from erro

    @property
    def total_paginas(self) -> int:
        return len(self._paginas)

    def obter_pagina(self, numero: int) -> Any:
        if not self._aberto:
            self.abrir()
        self._validar_numero_pagina(numero)
        from PIL import Image

        try:
            dados = self._arquivo.read(self._paginas[numero])
            imagem = Image.open(BytesIO(dados))
            imagem.load()
            return imagem.convert("RGB")
        except Exception as erro:
            raise ValueError(f"Não foi possível extrair a página do CBR: {erro}") from erro

    def fechar(self) -> None:
        if self._arquivo:
            self._arquivo.close()
        self._arquivo = None
        self._paginas = []
        self._aberto = False


class LeitorCB7(LeitorArquivo):
    def __init__(self, caminho: str | Path) -> None:
        super().__init__(caminho)
        self._temporario: tempfile.TemporaryDirectory[str] | None = None
        self._paginas: list[Path] = []

    def abrir(self) -> None:
        try:
            import py7zr

            self._temporario = tempfile.TemporaryDirectory(prefix="bookreadnet_cb7_")
            destino = Path(self._temporario.name)
            with py7zr.SevenZipFile(self.caminho, mode="r") as arquivo:
                arquivo.extractall(path=destino)
            self._paginas = sorted(
                [item for item in destino.rglob("*") if item.is_file() and item.suffix.lower() in FORMATOS_IMAGEM],
                key=lambda item: _chave_natural(str(item.relative_to(destino))),
            )
            if not self._paginas:
                self.fechar()
                raise ValueError("O arquivo CB7 não contém imagens.")
            self._aberto = True
        except ImportError as erro:
            self.fechar()
            raise RuntimeError("Instale a dependência py7zr para ler arquivos CB7.") from erro
        except Exception as erro:
            self.fechar()
            if isinstance(erro, ValueError):
                raise
            raise ValueError(f"Não foi possível abrir o CB7: {erro}") from erro

    @property
    def total_paginas(self) -> int:
        return len(self._paginas)

    def obter_pagina(self, numero: int) -> Any:
        if not self._aberto:
            self.abrir()
        self._validar_numero_pagina(numero)
        from PIL import Image

        with Image.open(self._paginas[numero]) as imagem:
            return imagem.convert("RGB")

    def fechar(self) -> None:
        self._paginas = []
        if self._temporario:
            self._temporario.cleanup()
        self._temporario = None
        self._aberto = False


@dataclass(frozen=True)
class TokenEPUB:
    tipo: str
    conteudo: str
    estilos: tuple[str, ...] = ()
    alternativa: str = ""


@dataclass(frozen=True)
class CapituloEPUB:
    titulo: str
    caminho: str
    tokens: tuple[TokenEPUB, ...]


class _ParserConteudoEPUB(HTMLParser):
    BLOCOS = {"p", "div", "section", "article", "header", "footer", "blockquote", "li", "h1", "h2", "h3", "h4"}
    ESTILOS = {"strong": "negrito", "b": "negrito", "em": "italico", "i": "italico", "h1": "titulo1", "h2": "titulo2", "h3": "titulo3", "blockquote": "citacao"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tokens: list[TokenEPUB] = []
        self._pilha: list[tuple[str, tuple[str, ...]]] = []
        self._ignorar = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "iframe", "object"}:
            self._ignorar += 1
            return
        if self._ignorar:
            return
        self._pilha.append((tag, self._estilos_atributos(attrs)))
        if tag in self.BLOCOS:
            self._quebra_linha()
        if tag == "br":
            self._adicionar_texto("\n")
        elif tag == "img":
            atributos = dict(attrs)
            origem = atributos.get("src") or atributos.get("data-src") or ""
            if origem:
                self.tokens.append(TokenEPUB("imagem", origem, alternativa=atributos.get("alt") or ""))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "iframe", "object"}:
            self._ignorar = max(0, self._ignorar - 1)
            return
        if self._ignorar:
            return
        if tag in self.BLOCOS:
            self._quebra_linha(dupla=tag in {"p", "div", "section", "article", "blockquote"})
        for indice in range(len(self._pilha) - 1, -1, -1):
            if self._pilha[indice][0] == tag:
                del self._pilha[indice]
                break

    def handle_data(self, data: str) -> None:
        if self._ignorar:
            return
        texto = re.sub(r"[\t\r\f\v ]+", " ", data)
        if texto.strip() or "\n" in texto:
            self._adicionar_texto(texto)

    def _adicionar_texto(self, texto: str) -> None:
        estilos_ativos: list[str] = []
        for tag, estilos_adicionais in self._pilha:
            if tag in self.ESTILOS:
                estilos_ativos.append(self.ESTILOS[tag])
            estilos_ativos.extend(estilos_adicionais)
        estilos = tuple(dict.fromkeys(estilos_ativos))
        if self.tokens and self.tokens[-1].tipo == "texto" and self.tokens[-1].estilos == estilos:
            anterior = self.tokens[-1]
            self.tokens[-1] = TokenEPUB("texto", anterior.conteudo + texto, estilos)
        else:
            self.tokens.append(TokenEPUB("texto", texto, estilos))

    @staticmethod
    def _estilos_atributos(attrs: list[tuple[str, str | None]]) -> tuple[str, ...]:
        atributos = dict(attrs)
        alinhamento = (atributos.get("align") or "").lower()
        estilo_inline = atributos.get("style") or ""
        encontrado = re.search(r"text-align\s*:\s*(left|center|right|justify)", estilo_inline, re.IGNORECASE)
        if encontrado:
            alinhamento = encontrado.group(1).lower()
        if alinhamento in {"left", "center", "right", "justify"}:
            return (f"alinhamento_{alinhamento}",)
        return ()

    def _quebra_linha(self, dupla: bool = False) -> None:
        quantidade = 2 if dupla else 1
        if not self.tokens:
            return
        ultimo = self.tokens[-1]
        if ultimo.tipo != "texto":
            self.tokens.append(TokenEPUB("texto", "\n" * quantidade))
            return
        faltantes = quantidade - len(ultimo.conteudo) + len(ultimo.conteudo.rstrip("\n"))
        if faltantes > 0:
            self.tokens[-1] = TokenEPUB("texto", ultimo.conteudo + "\n" * faltantes, ultimo.estilos)


class _ParserSumarioEPUB(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.itens: list[tuple[str, str]] = []
        self._nivel_nav = 0
        self._nivel_elemento = 0
        self._em_link = False
        self._href = ""
        self._texto: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        atributos = dict(attrs)
        if tag == "nav" and "toc" in (atributos.get("epub:type") or atributos.get("type") or "").split():
            self._nivel_nav = self._nivel_elemento + 1
        self._nivel_elemento += 1
        if self._nivel_nav and tag == "a" and atributos.get("href"):
            self._em_link = True
            self._href = atributos["href"] or ""
            self._texto = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._em_link:
            titulo = " ".join("".join(self._texto).split())
            if titulo:
                self.itens.append((self._href, titulo))
            self._em_link = False
        if self._nivel_nav and self._nivel_elemento == self._nivel_nav and tag == "nav":
            self._nivel_nav = 0
        self._nivel_elemento = max(0, self._nivel_elemento - 1)

    def handle_data(self, data: str) -> None:
        if self._em_link:
            self._texto.append(data)


class LeitorEPUB(LeitorArquivo):
    LIMITE_RECURSO = 30 * 1024 * 1024

    def __init__(self, caminho: str | Path) -> None:
        super().__init__(caminho)
        self._arquivo: ZipFile | None = None
        self._caminho_opf = ""
        self._manifesto: dict[str, dict[str, str]] = {}
        self._capitulos: list[str] = []
        self._titulos_capitulos: list[str] = []
        self._caminho_capa = ""
        self._metadados: dict[str, str] = {}
        self._recursos_criptografados: set[str] = set()

    def abrir(self) -> None:
        try:
            self._manifesto.clear()
            self._capitulos.clear()
            self._titulos_capitulos.clear()
            self._caminho_capa = ""
            self._metadados.clear()
            self._recursos_criptografados.clear()
            self._arquivo = ZipFile(self.caminho)
            self._validar_mimetype()
            self._caminho_opf = self._localizar_opf()
            self._carregar_pacote()
            if not self._capitulos:
                raise ValueError("O EPUB não possui capítulos em uma ordem de leitura válida.")
            self._carregar_criptografia()
            if any(capitulo in self._recursos_criptografados for capitulo in self._capitulos):
                raise ValueError("Este EPUB possui conteúdo protegido por DRM e não pode ser lido pelo BookReadNet.")
            self._aberto = True
        except (BadZipFile, ElementTree.ParseError, KeyError, OSError) as erro:
            self.fechar()
            raise ValueError(f"Não foi possível abrir o EPUB: {erro}") from erro
        except ValueError:
            self.fechar()
            raise

    @property
    def total_paginas(self) -> int:
        return len(self._capitulos)

    @property
    def titulos_capitulos(self) -> list[str]:
        return list(self._titulos_capitulos)

    @property
    def metadados(self) -> dict[str, str]:
        return dict(self._metadados)

    def obter_pagina(self, numero: int) -> CapituloEPUB:
        if not self._aberto:
            self.abrir()
        self._validar_numero_pagina(numero)
        caminho = self._capitulos[numero]
        dados = self._ler_recurso(caminho)
        parser = _ParserConteudoEPUB()
        parser.feed(self._decodificar_texto(dados))
        tokens: list[TokenEPUB] = []
        for token in parser.tokens:
            if token.tipo != "imagem":
                tokens.append(token)
                continue
            recurso = self._resolver_caminho(caminho, token.conteudo)
            if recurso and self._recurso_interno(recurso):
                tokens.append(TokenEPUB("imagem", recurso, alternativa=token.alternativa))
        return CapituloEPUB(self._titulos_capitulos[numero], caminho, tuple(tokens))

    def obter_imagem(self, caminho: str) -> Any:
        from PIL import Image

        dados = self._ler_recurso(caminho)
        with Image.open(BytesIO(dados)) as imagem:
            imagem.load()
            return imagem.convert("RGB")

    def obter_capa(self) -> Any:
        if not self._aberto:
            self.abrir()
        if not self._caminho_capa:
            return None
        return self.obter_imagem(self._caminho_capa)

    def fechar(self) -> None:
        if self._arquivo:
            self._arquivo.close()
        self._arquivo = None
        self._aberto = False

    def _validar_mimetype(self) -> None:
        if self._arquivo is None:
            raise ValueError("O EPUB não está aberto.")
        try:
            mimetype = self._arquivo.read("mimetype").decode("ascii").strip()
        except KeyError as erro:
            raise ValueError("O arquivo não contém o identificador mimetype do EPUB.") from erro
        if mimetype != "application/epub+zip":
            raise ValueError("O arquivo selecionado não é um EPUB válido.")

    def _localizar_opf(self) -> str:
        raiz = ElementTree.fromstring(self._ler_recurso("META-INF/container.xml"))
        rootfile = raiz.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("O EPUB não informa seu documento OPF.")
        caminho = self._normalizar_caminho(rootfile.get("full-path") or "")
        if not self._recurso_interno(caminho):
            raise ValueError("O caminho do documento OPF é inseguro.")
        return caminho

    def _carregar_pacote(self) -> None:
        raiz = ElementTree.fromstring(self._ler_recurso(self._caminho_opf))
        metadados = raiz.find(".//{*}metadata")
        self._metadados = {
            "titulo": self._texto_metadado(metadados, "title"),
            "autor": self._texto_metadado(metadados, "creator"),
            "idioma": self._texto_metadado(metadados, "language"),
            "editora": self._texto_metadado(metadados, "publisher"),
            "isbn": self._texto_metadado(metadados, "identifier"),
            "descricao": self._texto_metadado(metadados, "description"),
            "layout": "fluido",
        }
        if metadados is not None:
            for meta in metadados.findall("{*}meta"):
                propriedade = meta.get("property") or meta.get("name") or ""
                valor = (meta.text or meta.get("content") or "").strip()
                if propriedade == "rendition:layout" and valor == "pre-paginated":
                    self._metadados["layout"] = "fixo"

        manifesto = raiz.find(".//{*}manifest")
        if manifesto is None:
            raise ValueError("O EPUB não possui manifesto.")
        for item in manifesto.findall("{*}item"):
            identificador = item.get("id") or ""
            href = item.get("href") or ""
            if not identificador or not href:
                continue
            caminho = self._resolver_caminho(self._caminho_opf, href)
            if not caminho:
                continue
            self._manifesto[identificador] = {
                "caminho": caminho,
                "tipo": item.get("media-type") or "",
                "propriedades": item.get("properties") or "",
            }
            propriedades = (item.get("properties") or "").split()
            if "cover-image" in propriedades:
                self._caminho_capa = caminho

        self._localizar_capa_legada(metadados)
        spine = raiz.find(".//{*}spine")
        if spine is None:
            raise ValueError("O EPUB não possui spine.")
        for itemref in spine.findall("{*}itemref"):
            item = self._manifesto.get(itemref.get("idref") or "")
            if item and item["tipo"] in {"application/xhtml+xml", "image/svg+xml"}:
                self._capitulos.append(item["caminho"])

        titulos = self._carregar_sumario()
        self._titulos_capitulos = [
            titulos.get(caminho, self._titulo_por_caminho(caminho)) for caminho in self._capitulos
        ]

    def _localizar_capa_legada(self, metadados: ElementTree.Element | None) -> None:
        if self._caminho_capa or metadados is None:
            return
        for meta in metadados.findall("{*}meta"):
            if meta.get("name") == "cover" and meta.get("content") in self._manifesto:
                self._caminho_capa = self._manifesto[meta.get("content") or ""]["caminho"]
                return

    def _carregar_sumario(self) -> dict[str, str]:
        titulos: dict[str, str] = {}
        item_nav = next(
            (item for item in self._manifesto.values() if "nav" in item["propriedades"].split()),
            None,
        )
        if item_nav:
            parser = _ParserSumarioEPUB()
            parser.feed(self._decodificar_texto(self._ler_recurso(item_nav["caminho"])))
            for href, titulo in parser.itens:
                caminho = self._resolver_caminho(item_nav["caminho"], href)
                if caminho:
                    titulos[caminho] = titulo
            return titulos

        item_ncx = next(
            (item for item in self._manifesto.values() if item["tipo"] == "application/x-dtbncx+xml"),
            None,
        )
        if item_ncx:
            raiz = ElementTree.fromstring(self._ler_recurso(item_ncx["caminho"]))
            for ponto in raiz.findall(".//{*}navPoint"):
                texto = ponto.find(".//{*}navLabel/{*}text")
                conteudo = ponto.find("{*}content")
                if texto is not None and conteudo is not None and conteudo.get("src"):
                    caminho = self._resolver_caminho(item_ncx["caminho"], conteudo.get("src") or "")
                    if caminho:
                        titulos[caminho] = " ".join((texto.text or "").split())
        return titulos

    def _carregar_criptografia(self) -> None:
        if self._arquivo is None or "META-INF/encryption.xml" not in self._arquivo.namelist():
            return
        raiz = ElementTree.fromstring(self._ler_recurso("META-INF/encryption.xml"))
        for referencia in raiz.findall(".//{*}CipherReference"):
            uri = unquote(referencia.get("URI") or "")
            candidato = self._normalizar_caminho(urlsplit(uri).path)
            if candidato in self._arquivo.namelist():
                self._recursos_criptografados.add(candidato)
                continue
            resolvido = self._resolver_caminho("META-INF/encryption.xml", uri)
            if resolvido:
                self._recursos_criptografados.add(resolvido)

    def _ler_recurso(self, caminho: str) -> bytes:
        if self._arquivo is None:
            raise ValueError("O arquivo EPUB não está aberto.")
        caminho = self._normalizar_caminho(caminho)
        if not self._recurso_interno(caminho):
            raise ValueError("O EPUB tentou acessar um caminho inseguro.")
        try:
            info = self._arquivo.getinfo(caminho)
        except KeyError as erro:
            raise ValueError(f"Recurso ausente no EPUB: {caminho}") from erro
        if info.file_size > self.LIMITE_RECURSO:
            raise ValueError(f"Recurso muito grande dentro do EPUB: {caminho}")
        return self._arquivo.read(info)

    def _resolver_caminho(self, base: str, referencia: str) -> str:
        partes = urlsplit(referencia)
        if partes.scheme or partes.netloc:
            return ""
        referencia_limpa = unquote(partes.path)
        if not referencia_limpa:
            return self._normalizar_caminho(base)
        caminho = posixpath.join(posixpath.dirname(base), referencia_limpa)
        caminho = self._normalizar_caminho(caminho)
        return caminho if self._recurso_interno(caminho) else ""

    @staticmethod
    def _normalizar_caminho(caminho: str) -> str:
        return posixpath.normpath(caminho.replace("\\", "/")).lstrip("/")

    @staticmethod
    def _recurso_interno(caminho: str) -> bool:
        return bool(caminho) and caminho != ".." and not caminho.startswith("../") and ":" not in caminho

    @staticmethod
    def _texto_metadado(elemento: ElementTree.Element | None, nome: str) -> str:
        if elemento is None:
            return ""
        encontrado = elemento.find(f"{{*}}{nome}")
        return " ".join("".join(encontrado.itertext()).split()) if encontrado is not None else ""

    @staticmethod
    def _decodificar_texto(dados: bytes) -> str:
        for codificacao in ("utf-8", "utf-16", "latin-1"):
            try:
                return dados.decode(codificacao)
            except UnicodeDecodeError:
                continue
        return dados.decode("utf-8", errors="replace")

    @staticmethod
    def _titulo_por_caminho(caminho: str) -> str:
        return Path(caminho).stem.replace("_", " ").replace("-", " ").strip().title()


class FabricaLeitores:
    _leitores = {
        ".pdf": LeitorPDF,
        ".cbz": LeitorCBZ,
        ".cbr": LeitorCBR,
        ".cb7": LeitorCB7,
        ".epub": LeitorEPUB,
    }

    @classmethod
    def criar(cls, caminho: str | Path) -> LeitorArquivo:
        arquivo = validar_arquivo(caminho)
        classe = cls._leitores.get(arquivo.suffix.lower())
        if classe is None:
            raise ValueError("Não existe leitor para esse formato.")
        leitor = classe(arquivo)
        leitor.abrir()
        return leitor
