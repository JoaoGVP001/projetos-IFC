from __future__ import annotations

import json
from pathlib import Path

from modelos import ObraDigital, Usuario, obra_from_dict, usuario_from_dict


class RepositorioJSON:
    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    def salvar(self, obras: list[ObraDigital], usuario: Usuario) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = {
            "versao": 2,
            "obras": [obra.to_dict() for obra in obras],
            "usuario": usuario.to_dict(),
        }
        temporario = self.caminho.with_suffix(".tmp")
        temporario.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporario.replace(self.caminho)

    def carregar(self) -> tuple[list[ObraDigital], Usuario]:
        if not self.caminho.exists():
            return [], Usuario("Leitor local")
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            obras = [obra_from_dict(item) for item in dados.get("obras", [])]
            usuario = usuario_from_dict(dados.get("usuario", {}))
            return obras, usuario
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as erro:
            raise ValueError(f"Não foi possível carregar os dados salvos: {erro}") from erro
