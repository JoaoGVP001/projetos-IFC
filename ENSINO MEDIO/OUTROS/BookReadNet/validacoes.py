from __future__ import annotations

from pathlib import Path


FORMATOS_ACEITOS = (".pdf", ".cbz", ".cbr", ".cb7", ".epub")
FORMATOS_IMAGEM = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif")


def validar_arquivo(caminho: str | Path) -> Path:
    arquivo = Path(caminho).expanduser()
    if not arquivo.exists() or not arquivo.is_file():
        raise ValueError("O arquivo selecionado não existe.")
    if arquivo.suffix.lower() not in FORMATOS_ACEITOS:
        formatos = ", ".join(FORMATOS_ACEITOS)
        raise ValueError(f"Formato não suportado. Use: {formatos}.")
    if arquivo.stat().st_size == 0:
        raise ValueError("O arquivo selecionado está vazio.")
    return arquivo.resolve()


def validar_capa(caminho: str | Path) -> Path:
    capa = Path(caminho).expanduser()
    if not capa.exists() or not capa.is_file():
        raise ValueError("O arquivo de capa não existe.")
    if capa.suffix.lower() not in FORMATOS_IMAGEM:
        raise ValueError("A capa deve ser uma imagem JPG, PNG, WEBP, BMP ou GIF.")
    return capa.resolve()


def validar_titulo(titulo: str) -> str:
    titulo = titulo.strip()
    if not titulo:
        raise ValueError("O título da obra é obrigatório.")
    return titulo
