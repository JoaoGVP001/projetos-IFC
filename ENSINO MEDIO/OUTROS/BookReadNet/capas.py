from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from leitor import FabricaLeitores
from validacoes import validar_capa


class ServicoCapas:
    def __init__(self, pasta_capas: str | Path, pasta_miniaturas: str | Path) -> None:
        self.pasta_capas = Path(pasta_capas).resolve()
        self.pasta_miniaturas = Path(pasta_miniaturas).resolve()
        self.pasta_capas.mkdir(parents=True, exist_ok=True)
        self.pasta_miniaturas.mkdir(parents=True, exist_ok=True)

    def copiar_capa(self, origem: str | Path, id_obra: str) -> str:
        arquivo = validar_capa(origem)
        self._verificar_imagem(arquivo)
        destino = self.pasta_capas / f"{id_obra}_manual{arquivo.suffix.lower()}"
        if arquivo.resolve() != destino.resolve():
            shutil.copy2(arquivo, destino)
        self.invalidar_miniaturas(id_obra)
        return str(destino.resolve())

    def extrair_capa(self, caminho_obra: str | Path, id_obra: str) -> str:
        leitor = None
        try:
            leitor = FabricaLeitores.criar(caminho_obra)
            imagem = leitor.obter_capa() if hasattr(leitor, "obter_capa") else leitor.obter_pagina(0)
            if imagem is None:
                raise ValueError("A obra não possui uma capa interna.")
            imagem = self._normalizar_imagem(imagem)
            imagem.thumbnail((1200, 1800), self._filtro_redimensionamento())
            destino = self.pasta_capas / f"{id_obra}_automatica.jpg"
            imagem.save(destino, format="JPEG", quality=88, optimize=True)
            self.invalidar_miniaturas(id_obra)
            return str(destino.resolve())
        except (OSError, RuntimeError, ValueError):
            return ""
        finally:
            if leitor is not None:
                leitor.fechar()

    def substituir_capa(self, id_obra: str, capa_atual: str, nova_capa: str) -> str:
        destino = self.copiar_capa(nova_capa, id_obra)
        if capa_atual and Path(capa_atual).resolve() != Path(destino).resolve():
            self._excluir_gerenciado(capa_atual)
        return destino

    def remover_capa(self, id_obra: str, caminho_capa: str) -> None:
        if caminho_capa:
            self._excluir_gerenciado(caminho_capa)
        self.invalidar_miniaturas(id_obra)

    def obter_miniatura(
        self,
        id_obra: str,
        titulo: str,
        caminho_capa: str,
        tamanho: tuple[int, int] = (160, 230),
    ) -> Any:
        from PIL import Image

        largura, altura = tamanho
        capa = Path(caminho_capa) if caminho_capa else None
        cache = self.pasta_miniaturas / f"{id_obra}_{largura}x{altura}.jpg"
        if capa and capa.exists():
            if not cache.exists() or cache.stat().st_mtime < capa.stat().st_mtime:
                with Image.open(capa) as imagem:
                    miniatura = self._ajustar_capa(imagem, tamanho)
                    miniatura.save(cache, format="JPEG", quality=88, optimize=True)
            with Image.open(cache) as miniatura_salva:
                return miniatura_salva.copy()
        return self.criar_capa_padrao(titulo, tamanho)

    def criar_capa_padrao(self, titulo: str, tamanho: tuple[int, int]) -> Any:
        from PIL import Image, ImageDraw, ImageFont

        paleta = (
            (23, 35, 45),
            (45, 77, 86),
            (132, 73, 54),
            (80, 91, 64),
        )
        cor = paleta[sum(ord(letra) for letra in titulo) % len(paleta)]
        imagem = Image.new("RGB", tamanho, cor)
        desenho = ImageDraw.Draw(imagem)
        largura, altura = tamanho
        desenho.rectangle((0, altura - 48, largura, altura), fill=(231, 100, 59))
        desenho.line((16, 24, largura - 16, 24), fill=(217, 164, 65), width=3)

        inicial = (titulo.strip()[:1] or "B").upper()
        fonte_grande = self._carregar_fonte(max(34, largura // 3), negrito=True)
        fonte_pequena = self._carregar_fonte(max(10, largura // 14), negrito=True)
        caixa = desenho.textbbox((0, 0), inicial, font=fonte_grande)
        texto_largura = caixa[2] - caixa[0]
        texto_altura = caixa[3] - caixa[1]
        desenho.text(
            ((largura - texto_largura) / 2, (altura - texto_altura) / 2 - 24),
            inicial,
            fill=(255, 253, 248),
            font=fonte_grande,
        )
        desenho.text((14, altura - 33), "BOOKREADNET", fill=(255, 255, 255), font=fonte_pequena)
        return imagem

    def invalidar_miniaturas(self, id_obra: str) -> None:
        for arquivo in self.pasta_miniaturas.glob(f"{id_obra}_*"):
            if arquivo.is_file():
                arquivo.unlink(missing_ok=True)

    @staticmethod
    def _verificar_imagem(caminho: Path) -> None:
        try:
            from PIL import Image

            with Image.open(caminho) as imagem:
                imagem.verify()
        except (OSError, ValueError) as erro:
            raise ValueError("A capa selecionada não é uma imagem válida.") from erro

    @classmethod
    def _ajustar_capa(cls, imagem: Any, tamanho: tuple[int, int]) -> Any:
        from PIL import ImageOps

        normalizada = cls._normalizar_imagem(imagem)
        return ImageOps.fit(
            normalizada,
            tamanho,
            method=cls._filtro_redimensionamento(),
            centering=(0.5, 0.45),
        )

    @staticmethod
    def _normalizar_imagem(imagem: Any) -> Any:
        from PIL import ImageOps

        return ImageOps.exif_transpose(imagem).convert("RGB")

    @staticmethod
    def _filtro_redimensionamento() -> Any:
        from PIL import Image

        return Image.Resampling.LANCZOS

    @staticmethod
    def _carregar_fonte(tamanho: int, negrito: bool = False) -> Any:
        from PIL import ImageFont

        nomes = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if negrito else ("arial.ttf", "DejaVuSans.ttf")
        for nome in nomes:
            try:
                return ImageFont.truetype(nome, tamanho)
            except OSError:
                continue
        return ImageFont.load_default()

    def _excluir_gerenciado(self, caminho: str | Path) -> None:
        arquivo = Path(caminho).resolve()
        try:
            arquivo.relative_to(self.pasta_capas)
        except ValueError:
            return
        arquivo.unlink(missing_ok=True)
