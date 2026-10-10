from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class StatusLeitura(str, Enum):
    NAO_INICIADO = "Não iniciado"
    EM_LEITURA = "Em leitura"
    LIDO = "Lido"


class ObraDigital(ABC):
    def __init__(
        self,
        id_obra: str,
        titulo: str,
        autor: str,
        caminho_arquivo: str,
        categoria: str = "Sem categoria",
        serie: str = "",
        editora: str = "",
        idioma: str = "Português",
        caminho_capa: str = "",
        favorito: bool = False,
        status_leitura: StatusLeitura | str = StatusLeitura.NAO_INICIADO,
        numero_paginas: int = 0,
        data_adicao: str | None = None,
    ) -> None:
        self.id_obra = id_obra
        self.titulo = titulo
        self.autor = autor
        self.caminho_arquivo = caminho_arquivo
        self.categoria = categoria
        self.serie = serie
        self.editora = editora
        self.idioma = idioma
        self.caminho_capa = caminho_capa
        self.favorito = favorito
        self.status_leitura = status_leitura
        self.numero_paginas = numero_paginas
        self.data_adicao = data_adicao or datetime.now().isoformat(timespec="seconds")

    @property
    def id_obra(self) -> str:
        return self.__id_obra

    @id_obra.setter
    def id_obra(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("O ID da obra não pode estar vazio.")
        self.__id_obra = valor

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("O título não pode estar vazio.")
        self.__titulo = valor

    @property
    def autor(self) -> str:
        return self.__autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self.__autor = valor.strip() or "Autor desconhecido"

    @property
    def caminho_arquivo(self) -> str:
        return self.__caminho_arquivo

    @caminho_arquivo.setter
    def caminho_arquivo(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("O arquivo da obra é obrigatório.")
        self.__caminho_arquivo = valor

    @property
    def caminho_capa(self) -> str:
        return self.__caminho_capa

    @caminho_capa.setter
    def caminho_capa(self, valor: str) -> None:
        self.__caminho_capa = str(valor).strip()

    @property
    def categoria(self) -> str:
        return self.__categoria

    @categoria.setter
    def categoria(self, valor: str) -> None:
        self.__categoria = valor.strip() or "Sem categoria"

    @property
    def editora(self) -> str:
        return self.__editora

    @editora.setter
    def editora(self, valor: str) -> None:
        self.__editora = valor.strip()

    @property
    def serie(self) -> str:
        return self.__serie

    @serie.setter
    def serie(self, valor: str) -> None:
        self.__serie = valor.strip()

    @property
    def idioma(self) -> str:
        return self.__idioma

    @idioma.setter
    def idioma(self, valor: str) -> None:
        self.__idioma = valor.strip() or "Português"

    @property
    def favorito(self) -> bool:
        return self.__favorito

    @favorito.setter
    def favorito(self, valor: bool) -> None:
        self.__favorito = bool(valor)

    @property
    def status_leitura(self) -> StatusLeitura:
        return self.__status_leitura

    @status_leitura.setter
    def status_leitura(self, valor: StatusLeitura | str) -> None:
        self.__status_leitura = StatusLeitura(valor)

    @property
    def numero_paginas(self) -> int:
        return self.__numero_paginas

    @numero_paginas.setter
    def numero_paginas(self, valor: int) -> None:
        valor = int(valor)
        if valor < 0:
            raise ValueError("O número de páginas não pode ser negativo.")
        self.__numero_paginas = valor

    @property
    def formato(self) -> str:
        return Path(self.caminho_arquivo).suffix.lower().lstrip(".").upper()

    @abstractmethod
    def obter_tipo(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def dados_especificos(self) -> dict[str, Any]:
        raise NotImplementedError

    def exibir_dados(self) -> str:
        favorito = "★" if self.favorito else " "
        return (
            f"{favorito} {self.titulo} | {self.autor} | {self.obter_tipo()} | "
            f"{self.formato} | {self.status_leitura.value}"
        )

    def to_dict(self) -> dict[str, Any]:
        dados = {
            "id_obra": self.id_obra,
            "titulo": self.titulo,
            "autor": self.autor,
            "caminho_arquivo": self.caminho_arquivo,
            "categoria": self.categoria,
            "serie": self.serie,
            "editora": self.editora,
            "idioma": self.idioma,
            "caminho_capa": self.caminho_capa,
            "favorito": self.favorito,
            "status_leitura": self.status_leitura.value,
            "numero_paginas": self.numero_paginas,
            "data_adicao": self.data_adicao,
            "tipo": self.obter_tipo(),
        }
        dados.update(self.dados_especificos())
        return dados


class HQ(ObraDigital):
    def __init__(self, *args: Any, universo: str = "", numero_edicao: str = "", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.universo = universo.strip()
        self.numero_edicao = str(numero_edicao).strip()

    def obter_tipo(self) -> str:
        return "HQ"

    def dados_especificos(self) -> dict[str, Any]:
        return {"universo": self.universo, "numero_edicao": self.numero_edicao}


class Manga(ObraDigital):
    def __init__(
        self,
        *args: Any,
        volume: str = "",
        numero_capitulo: str = "",
        sentido_leitura: str = "Direita para esquerda",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.volume = str(volume).strip()
        self.numero_capitulo = str(numero_capitulo).strip()
        self.sentido_leitura = sentido_leitura.strip() or "Direita para esquerda"

    def obter_tipo(self) -> str:
        return "Mangá"

    def dados_especificos(self) -> dict[str, Any]:
        return {
            "volume": self.volume,
            "numero_capitulo": self.numero_capitulo,
            "sentido_leitura": self.sentido_leitura,
        }


class LivroDigital(ObraDigital):
    def __init__(self, *args: Any, isbn: str = "", edicao: str = "", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.isbn = isbn.strip()
        self.edicao = str(edicao).strip()

    def obter_tipo(self) -> str:
        return "Livro digital"

    def dados_especificos(self) -> dict[str, Any]:
        return {"isbn": self.isbn, "edicao": self.edicao}


@dataclass(frozen=True)
class Categoria:
    nome: str

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("O nome da categoria não pode estar vazio.")


class Serie:
    def __init__(self, nome: str, descricao: str = "") -> None:
        if not nome.strip():
            raise ValueError("O nome da série não pode estar vazio.")
        self.nome = nome.strip()
        self.descricao = descricao.strip()
        self.__obras: list[ObraDigital] = []

    @property
    def obras(self) -> list[ObraDigital]:
        return list(self.__obras)

    def adicionar_obra(self, obra: ObraDigital) -> None:
        if obra not in self.__obras:
            self.__obras.append(obra)

    def remover_obra(self, obra: ObraDigital) -> None:
        if obra in self.__obras:
            self.__obras.remove(obra)


class ProgressoLeitura:
    def __init__(
        self,
        obra_id: str,
        pagina_atual: int = 0,
        total_paginas: int = 0,
        ultima_leitura: str | None = None,
        capitulo_atual: int = 0,
        total_capitulos: int = 0,
        posicao_capitulo: float = 0.0,
        tipo_posicao: str = "pagina",
    ) -> None:
        self.obra_id = obra_id
        self.total_paginas = total_paginas
        self.pagina_atual = pagina_atual
        self.capitulo_atual = int(capitulo_atual)
        self.total_capitulos = int(total_capitulos)
        self.posicao_capitulo = float(posicao_capitulo)
        self.tipo_posicao = tipo_posicao
        self.ultima_leitura = ultima_leitura

    @property
    def total_paginas(self) -> int:
        return self.__total_paginas

    @total_paginas.setter
    def total_paginas(self, valor: int) -> None:
        valor = int(valor)
        if valor < 0:
            raise ValueError("O total de páginas não pode ser negativo.")
        self.__total_paginas = valor

    @property
    def pagina_atual(self) -> int:
        return self.__pagina_atual

    @pagina_atual.setter
    def pagina_atual(self, valor: int) -> None:
        valor = int(valor)
        if valor < 0:
            raise ValueError("A página atual não pode ser negativa.")
        if self.total_paginas and valor > self.total_paginas:
            raise ValueError("A página atual não pode ultrapassar o total de páginas.")
        self.__pagina_atual = valor

    @property
    def porcentagem(self) -> float:
        if self.tipo_posicao == "capitulo":
            if not self.total_capitulos:
                return 0.0
            concluido = max(0, self.capitulo_atual - 1) + self.posicao_capitulo
            return round(min(100.0, (concluido / self.total_capitulos) * 100), 1)
        if not self.total_paginas:
            return 0.0
        return round((self.pagina_atual / self.total_paginas) * 100, 1)

    @property
    def status(self) -> StatusLeitura:
        if self.porcentagem >= 100:
            return StatusLeitura.LIDO
        if self.porcentagem > 0 or self.capitulo_atual > 0:
            return StatusLeitura.EM_LEITURA
        return StatusLeitura.NAO_INICIADO

    def atualizar_pagina(self, pagina: int, total_paginas: int | None = None) -> None:
        if total_paginas is not None:
            self.total_paginas = total_paginas
        self.pagina_atual = pagina
        self.tipo_posicao = "pagina"
        self.ultima_leitura = datetime.now().isoformat(timespec="seconds")

    def atualizar_capitulo(self, capitulo: int, total_capitulos: int, posicao: float = 0.0) -> None:
        capitulo = int(capitulo)
        total_capitulos = int(total_capitulos)
        posicao = float(posicao)
        if total_capitulos <= 0:
            raise ValueError("O EPUB deve possuir pelo menos um capítulo.")
        if capitulo < 1 or capitulo > total_capitulos:
            raise ValueError("O capítulo atual está fora dos limites da obra.")
        if posicao < 0 or posicao > 1:
            raise ValueError("A posição dentro do capítulo deve estar entre 0 e 1.")
        self.capitulo_atual = capitulo
        self.total_capitulos = total_capitulos
        self.posicao_capitulo = posicao
        self.pagina_atual = capitulo
        self.total_paginas = total_capitulos
        self.tipo_posicao = "capitulo"
        self.ultima_leitura = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        return {
            "obra_id": self.obra_id,
            "pagina_atual": self.pagina_atual,
            "total_paginas": self.total_paginas,
            "ultima_leitura": self.ultima_leitura,
            "capitulo_atual": self.capitulo_atual,
            "total_capitulos": self.total_capitulos,
            "posicao_capitulo": self.posicao_capitulo,
            "tipo_posicao": self.tipo_posicao,
        }


@dataclass(frozen=True)
class HistoricoLeitura:
    obra_id: str
    pagina: int
    data: str
    capitulo: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "obra_id": self.obra_id,
            "pagina": self.pagina,
            "data": self.data,
            "capitulo": self.capitulo,
        }


class Usuario:
    def __init__(
        self,
        nome: str,
        progressos: dict[str, ProgressoLeitura] | None = None,
        historico: list[HistoricoLeitura] | None = None,
    ) -> None:
        self.nome = nome
        self.__progressos = progressos or {}
        self.__historico = historico or []

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, valor: str) -> None:
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome do usuário não pode estar vazio.")
        self.__nome = valor

    @property
    def progressos(self) -> dict[str, ProgressoLeitura]:
        return dict(self.__progressos)

    @property
    def historico(self) -> list[HistoricoLeitura]:
        return list(self.__historico)

    def obter_progresso(self, obra_id: str) -> ProgressoLeitura:
        if obra_id not in self.__progressos:
            self.__progressos[obra_id] = ProgressoLeitura(obra_id)
        return self.__progressos[obra_id]

    def salvar_progresso(self, obra_id: str, pagina: int, total_paginas: int) -> ProgressoLeitura:
        progresso = self.obter_progresso(obra_id)
        progresso.atualizar_pagina(pagina, total_paginas)
        self.__historico.append(
            HistoricoLeitura(obra_id, pagina, datetime.now().isoformat(timespec="seconds"))
        )
        self.__historico = self.__historico[-100:]
        return progresso

    def salvar_progresso_epub(
        self,
        obra_id: str,
        capitulo: int,
        total_capitulos: int,
        posicao: float,
    ) -> ProgressoLeitura:
        progresso = self.obter_progresso(obra_id)
        progresso.atualizar_capitulo(capitulo, total_capitulos, posicao)
        self.__historico.append(
            HistoricoLeitura(
                obra_id,
                capitulo,
                datetime.now().isoformat(timespec="seconds"),
                capitulo=capitulo,
            )
        )
        self.__historico = self.__historico[-100:]
        return progresso

    def remover_dados_obra(self, obra_id: str) -> None:
        self.__progressos.pop(obra_id, None)
        self.__historico = [item for item in self.__historico if item.obra_id != obra_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nome": self.nome,
            "progressos": [item.to_dict() for item in self.__progressos.values()],
            "historico": [item.to_dict() for item in self.__historico],
        }


def obra_from_dict(dados: dict[str, Any]) -> ObraDigital:
    tipo = dados.get("tipo", "HQ")
    classes = {"HQ": HQ, "Mangá": Manga, "Livro digital": LivroDigital}
    classe = classes.get(tipo)
    if classe is None:
        raise ValueError(f"Tipo de obra desconhecido: {tipo}")

    comuns = {
        chave: dados.get(chave, padrao)
        for chave, padrao in {
            "id_obra": "",
            "titulo": "",
            "autor": "",
            "caminho_arquivo": "",
            "categoria": "Sem categoria",
            "serie": "",
            "editora": "",
            "idioma": "Português",
            "caminho_capa": "",
            "favorito": False,
            "status_leitura": StatusLeitura.NAO_INICIADO.value,
            "numero_paginas": 0,
            "data_adicao": None,
        }.items()
    }
    especificos = {
        HQ: {"universo": dados.get("universo", ""), "numero_edicao": dados.get("numero_edicao", "")},
        Manga: {
            "volume": dados.get("volume", ""),
            "numero_capitulo": dados.get("numero_capitulo", ""),
            "sentido_leitura": dados.get("sentido_leitura", "Direita para esquerda"),
        },
        LivroDigital: {"isbn": dados.get("isbn", ""), "edicao": dados.get("edicao", "")},
    }
    return classe(**comuns, **especificos[classe])


def usuario_from_dict(dados: dict[str, Any]) -> Usuario:
    progressos = {
        item["obra_id"]: ProgressoLeitura(**item)
        for item in dados.get("progressos", [])
    }
    historico = [HistoricoLeitura(**item) for item in dados.get("historico", [])]
    return Usuario(dados.get("nome", "Leitor local"), progressos, historico)
