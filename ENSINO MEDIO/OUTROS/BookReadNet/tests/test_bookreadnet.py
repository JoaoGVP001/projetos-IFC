from __future__ import annotations

import base64
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

import pytest

from leitor import FabricaLeitores, LeitorCB7, LeitorCBR, LeitorCBZ, LeitorEPUB, LeitorPDF
from modelos import Manga, ProgressoLeitura, StatusLeitura
from servicos import BibliotecaDigital
from validacoes import FORMATOS_ACEITOS, validar_arquivo


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def criar_cbz(caminho: Path) -> Path:
    with ZipFile(caminho, "w") as arquivo:
        arquivo.writestr("pagina_10.png", PNG_1X1)
        arquivo.writestr("pagina_2.png", PNG_1X1)
        arquivo.writestr("notas.txt", "ignorar")
    return caminho


def criar_epub(caminho: Path) -> Path:
    container = """<?xml version="1.0"?>
    <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
      <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
    </container>"""
    pacote = """<?xml version="1.0" encoding="UTF-8"?>
    <package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0">
      <metadata>
        <dc:identifier>978-00-BOOKREADNET</dc:identifier>
        <dc:title>Livro de Teste EPUB</dc:title>
        <dc:creator>Autora Exemplo</dc:creator>
        <dc:language>pt-BR</dc:language>
        <dc:publisher>Editora BookReadNet</dc:publisher>
      </metadata>
      <manifest>
        <item id="cover" href="images/cover.png" media-type="image/png" properties="cover-image"/>
        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
        <item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
        <item id="c2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
        <item id="img" href="images/page.png" media-type="image/png"/>
      </manifest>
      <spine><itemref idref="c1"/><itemref idref="c2"/></spine>
    </package>"""
    navegacao = """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
      <body><nav epub:type="toc"><ol>
        <li><a href="chapter1.xhtml">O começo</a></li>
        <li><a href="chapter2.xhtml">O final</a></li>
      </ol></nav></body></html>"""
    capitulo1 = """<html xmlns="http://www.w3.org/1999/xhtml"><body>
      <h1>Primeiro capítulo</h1><p>Texto <strong>importante</strong> da história.</p>
      <img src="images/page.png" alt="Ilustração interna"/>
      <img src="https://example.com/externa.png" alt="Externa"/>
      <script>conteudo_perigoso()</script>
    </body></html>"""
    capitulo2 = """<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>Fim</h1><p style="text-align: center">Segundo capítulo.</p></body></html>"""

    with ZipFile(caminho, "w") as arquivo:
        arquivo.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        arquivo.writestr("META-INF/container.xml", container)
        arquivo.writestr("OEBPS/content.opf", pacote)
        arquivo.writestr("OEBPS/nav.xhtml", navegacao)
        arquivo.writestr("OEBPS/chapter1.xhtml", capitulo1)
        arquivo.writestr("OEBPS/chapter2.xhtml", capitulo2)
        arquivo.writestr("OEBPS/images/cover.png", PNG_1X1)
        arquivo.writestr("OEBPS/images/page.png", PNG_1X1)
    return caminho


def criar_biblioteca(tmp_path: Path) -> BibliotecaDigital:
    return BibliotecaDigital("BookReadNet Teste", tmp_path)


def cadastrar_manga(biblioteca: BibliotecaDigital, arquivo: Path, titulo: str = "Berserk") -> Manga:
    obra = biblioteca.cadastrar_obra(
        tipo="Mangá",
        titulo=titulo,
        autor="Kentaro Miura",
        caminho_arquivo=str(arquivo),
        categoria="Fantasia",
        serie="Berserk",
        volume="1",
    )
    assert isinstance(obra, Manga)
    return obra


def test_formatos_principais_estao_habilitados() -> None:
    assert set(FORMATOS_ACEITOS) == {".pdf", ".cbz", ".cbr", ".cb7", ".epub"}


def test_validacao_rejeita_arquivo_inexistente(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="não existe"):
        validar_arquivo(tmp_path / "inexistente.cbz")


def test_cadastro_copia_arquivo_e_persiste_acervo(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)

    obra = cadastrar_manga(biblioteca, origem)
    recarregada = criar_biblioteca(tmp_path)

    assert Path(obra.caminho_arquivo).exists()
    assert Path(obra.caminho_arquivo).parent.name == "arquivos"
    assert len(recarregada.obras) == 1
    assert recarregada.obras[0].titulo == "Berserk"
    assert recarregada.obras[0].serie == "Berserk"
    assert Path(obra.caminho_capa).exists()
    assert Path(obra.caminho_capa).parent.name == "capas"


def test_impede_cadastro_duplicado_e_remove_copia_criada(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)
    cadastrar_manga(biblioteca, origem)

    with pytest.raises(ValueError, match="já está cadastrada"):
        cadastrar_manga(biblioteca, origem)

    assert len(list(biblioteca.pasta_arquivos.glob("*.cbz"))) == 1


def test_favoritos_busca_e_filtros(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)
    obra = cadastrar_manga(biblioteca, origem)

    assert biblioteca.pesquisar("miura") == [obra]
    assert biblioteca.filtrar(tipo="HQ") == []
    assert biblioteca.alternar_favorito(obra.id_obra) is True
    assert biblioteca.filtrar(somente_favoritos=True) == [obra]


def test_progresso_valida_paginas_e_altera_status() -> None:
    progresso = ProgressoLeitura("OBRA1")
    progresso.atualizar_pagina(2, 10)
    assert progresso.porcentagem == 20.0
    assert progresso.status == StatusLeitura.EM_LEITURA

    progresso.atualizar_pagina(10, 10)
    assert progresso.status == StatusLeitura.LIDO

    with pytest.raises(ValueError, match="ultrapassar"):
        progresso.atualizar_pagina(11, 10)


def test_servico_salva_progresso_e_historico(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)
    obra = cadastrar_manga(biblioteca, origem)

    progresso = biblioteca.salvar_progresso(obra.id_obra, 2, 2)
    recarregada = criar_biblioteca(tmp_path)

    assert progresso.status == StatusLeitura.LIDO
    assert obra.status_leitura == StatusLeitura.LIDO
    assert recarregada.obter_progresso(obra.id_obra).pagina_atual == 2
    assert "Berserk" in recarregada.listar_historico()[0]


def test_leitor_cbz_ordena_paginas_naturalmente(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "quadrinho.cbz")
    leitor = FabricaLeitores.criar(origem)

    assert isinstance(leitor, LeitorCBZ)
    assert leitor.total_paginas == 2
    assert leitor._paginas == ["pagina_2.png", "pagina_10.png"]
    assert leitor.obter_pagina(0).size == (1, 1)
    leitor.fechar()


def test_leitor_pdf_renderiza_pagina(tmp_path: Path) -> None:
    import fitz

    caminho = tmp_path / "quadrinho.pdf"
    documento = fitz.open()
    pagina = documento.new_page(width=300, height=400)
    pagina.insert_text((40, 60), "BookReadNet")
    documento.save(caminho)
    documento.close()

    leitor = FabricaLeitores.criar(caminho)

    assert isinstance(leitor, LeitorPDF)
    assert leitor.total_paginas == 1
    assert leitor.obter_pagina(0).width > 300
    leitor.fechar()


def test_leitor_cb7_extrai_imagens(tmp_path: Path) -> None:
    import py7zr

    imagem = tmp_path / "pagina_1.png"
    imagem.write_bytes(PNG_1X1)
    caminho = tmp_path / "quadrinho.cb7"
    with py7zr.SevenZipFile(caminho, "w") as arquivo:
        arquivo.write(imagem, arcname="pagina_1.png")

    leitor = FabricaLeitores.criar(caminho)

    assert isinstance(leitor, LeitorCB7)
    assert leitor.total_paginas == 1
    assert leitor.obter_pagina(0).size == (1, 1)
    leitor.fechar()


def test_fabrica_direciona_cbr_ao_leitor_rar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    caminho = tmp_path / "quadrinho.cbr"
    caminho.write_bytes(b"RAR de teste")
    monkeypatch.setattr(LeitorCBR, "abrir", lambda self: setattr(self, "_aberto", True))

    leitor = FabricaLeitores.criar(caminho)

    assert isinstance(leitor, LeitorCBR)
    leitor.fechar()


def test_exclusao_remove_progresso_e_arquivo_quando_confirmado(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)
    obra = cadastrar_manga(biblioteca, origem)
    arquivo_copiado = Path(obra.caminho_arquivo)
    biblioteca.salvar_progresso(obra.id_obra, 1, 2)

    biblioteca.excluir_obra(obra.id_obra, excluir_arquivo=True)

    assert biblioteca.obras == []
    assert not arquivo_copiado.exists()
    assert obra.id_obra not in biblioteca.usuario.progressos


def test_miniatura_tem_tamanho_padronizado(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)
    obra = cadastrar_manga(biblioteca, origem)

    miniatura = biblioteca.obter_miniatura(obra.id_obra, (160, 230))

    assert miniatura.size == (160, 230)
    assert any(biblioteca.pasta_miniaturas.glob(f"{obra.id_obra}_*.jpg"))


def test_usuario_pode_substituir_e_remover_capa(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    capa_manual = tmp_path / "capa.png"
    capa_manual.write_bytes(PNG_1X1)
    biblioteca = criar_biblioteca(tmp_path)
    obra = cadastrar_manga(biblioteca, origem)
    capa_automatica = Path(obra.caminho_capa)

    nova_capa = biblioteca.atualizar_capa(obra.id_obra, str(capa_manual))

    assert Path(nova_capa).exists()
    assert "manual" in Path(nova_capa).name
    assert not capa_automatica.exists()

    biblioteca.atualizar_capa(obra.id_obra)

    assert obra.caminho_capa == ""
    assert not Path(nova_capa).exists()
    assert biblioteca.obter_miniatura(obra.id_obra, (120, 180)).size == (120, 180)


def test_rejeita_arquivo_de_capa_corrompido(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    capa_invalida = tmp_path / "capa.png"
    capa_invalida.write_text("não é uma imagem", encoding="utf-8")
    biblioteca = criar_biblioteca(tmp_path)

    with pytest.raises(ValueError, match="imagem válida"):
        biblioteca.cadastrar_obra(
            tipo="Mangá",
            titulo="Berserk",
            autor="Kentaro Miura",
            caminho_arquivo=str(origem),
            caminho_capa=str(capa_invalida),
            volume="1",
        )

    assert list(biblioteca.pasta_arquivos.glob("*.cbz")) == []


def test_cadastro_respeita_escolha_de_nao_gerar_capa(tmp_path: Path) -> None:
    origem = criar_cbz(tmp_path / "berserk.cbz")
    biblioteca = criar_biblioteca(tmp_path)

    obra = biblioteca.cadastrar_obra(
        tipo="Mangá",
        titulo="Berserk",
        autor="Kentaro Miura",
        caminho_arquivo=str(origem),
        extrair_capa_automatica=False,
        volume="1",
    )

    assert obra.caminho_capa == ""
    assert biblioteca.obter_miniatura(obra.id_obra, (120, 180)).size == (120, 180)


def test_leitor_epub_carrega_metadados_sumario_conteudo_e_capa(tmp_path: Path) -> None:
    caminho = criar_epub(tmp_path / "livro.epub")

    leitor = FabricaLeitores.criar(caminho)

    assert isinstance(leitor, LeitorEPUB)
    assert leitor.total_paginas == 2
    assert leitor.metadados["titulo"] == "Livro de Teste EPUB"
    assert leitor.metadados["autor"] == "Autora Exemplo"
    assert leitor.titulos_capitulos == ["O começo", "O final"]
    assert leitor.obter_capa().size == (1, 1)

    capitulo = leitor.obter_pagina(0)
    textos = "".join(token.conteudo for token in capitulo.tokens if token.tipo == "texto")
    imagens = [token for token in capitulo.tokens if token.tipo == "imagem"]
    assert "Primeiro capítulo" in textos
    assert "conteudo_perigoso" not in textos
    assert len(imagens) == 1
    assert imagens[0].conteudo == "OEBPS/images/page.png"
    segundo_capitulo = leitor.obter_pagina(1)
    assert any("alinhamento_center" in token.estilos for token in segundo_capitulo.tokens)
    leitor.fechar()


def test_leitor_epub_rejeita_capitulo_protegido_por_drm(tmp_path: Path) -> None:
    caminho = criar_epub(tmp_path / "protegido.epub")
    criptografia = """<?xml version="1.0" encoding="UTF-8"?>
    <encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
                xmlns:enc="http://www.w3.org/2001/04/xmlenc#">
      <enc:EncryptedData>
        <enc:CipherData>
          <enc:CipherReference URI="OEBPS/chapter1.xhtml"/>
        </enc:CipherData>
      </enc:EncryptedData>
    </encryption>"""
    with ZipFile(caminho, "a") as arquivo:
        arquivo.writestr("META-INF/encryption.xml", criptografia)

    with pytest.raises(ValueError, match="DRM"):
        FabricaLeitores.criar(caminho)


def test_cadastro_epub_aproveita_metadados_e_capa_interna(tmp_path: Path) -> None:
    caminho = criar_epub(tmp_path / "livro.epub")
    biblioteca = criar_biblioteca(tmp_path)

    obra = biblioteca.cadastrar_obra(
        tipo="Livro digital",
        titulo="",
        autor="",
        caminho_arquivo=str(caminho),
    )

    assert obra.titulo == "Livro de Teste EPUB"
    assert obra.autor == "Autora Exemplo"
    assert obra.editora == "Editora BookReadNet"
    assert obra.idioma == "pt-BR"
    assert obra.isbn == "978-00-BOOKREADNET"
    assert Path(obra.caminho_capa).exists()


def test_progresso_epub_salva_capitulo_posicao_e_historico(tmp_path: Path) -> None:
    caminho = criar_epub(tmp_path / "livro.epub")
    biblioteca = criar_biblioteca(tmp_path)
    obra = biblioteca.cadastrar_obra("Livro digital", "", "", str(caminho))

    progresso = biblioteca.salvar_progresso_epub(obra.id_obra, 2, 4, 0.5)
    recarregada = criar_biblioteca(tmp_path)
    salvo = recarregada.obter_progresso(obra.id_obra)

    assert progresso.porcentagem == 37.5
    assert salvo.capitulo_atual == 2
    assert salvo.posicao_capitulo == 0.5
    assert salvo.tipo_posicao == "capitulo"
    assert "capítulo 2" in recarregada.listar_historico()[0]
