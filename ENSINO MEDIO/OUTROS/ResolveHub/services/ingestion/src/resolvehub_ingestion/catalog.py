from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
import unicodedata
from zipfile import ZipFile, ZipInfo

from .inventory import _is_symlink
from .policy import Decision, classify_entry

SENSITIVE_TITLE_PATTERN = re.compile(
    r"(?:\b(?:cliente|clientes|empresa|cpf|cnpj|e-?mail|telefone|celular|contato)\b|"
    r"\b\d{6,}\b|[\w.+-]+@[\w.-]+\.[a-z]{2,})",
    re.IGNORECASE,
)

STATUS_LABELS = {
    "include": "Pronto para extração",
    "review": "Revisão necessária",
    "defer": "Pendente de OCR ou mídia",
    "block": "Bloqueado por segurança",
    "skip": "Formato não suportado",
}

REASON_LABELS = {
    "supported_document": "Documento compatível com o MVP",
    "manual_review": "Requer validação antes da publicação",
    "future_ocr_or_media": "Reservado para uma etapa futura",
    "blocked_extension": "Formato protegido pela política de segurança",
    "secret_filename": "Possível credencial ou dado sensível no caminho",
    "size_limit": "Arquivo acima do limite permitido",
    "unsupported_extension": "Formato ainda não atendido",
    "unsafe_path": "Caminho inseguro dentro do pacote",
    "symlink": "Link simbólico não permitido",
}


def _clean_title(path: PurePosixPath) -> str:
    title = path.stem.replace("_", " ").strip(" .-_\t")
    title = unicodedata.normalize("NFKC", title)
    title = re.sub(r"\s+", " ", title)
    title = title.replace("�", "")
    return title[:180] or "Documento sem título"


def _category(path: PurePosixPath) -> str:
    normalized = "/".join(path.parts).casefold()
    if "1- copypasta" in normalized:
        return "Copypasta e configurações"
    if "2- procedimentos" in normalized:
        return "Procedimentos"
    if "3- help geral" in normalized:
        return "Help Geral"
    return "Outros"


def _system(path: PurePosixPath) -> str:
    normalized = "/".join(path.parts).casefold()
    if "zweb" in normalized:
        return "ZWeb"
    if "small" in normalized:
        return "Small Commerce"
    return "Interno"


def _should_mask_title(path: PurePosixPath, decision: Decision) -> bool:
    if decision.status != "include":
        return True
    return bool(SENSITIVE_TITLE_PATTERN.search(" ".join(path.parts)))


def _source_item(info: ZipInfo, ordinal: int) -> dict[str, object]:
    decision = classify_entry(
        info.filename,
        info.file_size,
        is_directory=info.is_dir(),
        is_symlink=_is_symlink(info),
    )
    path = PurePosixPath(info.filename.replace("\\", "/"))
    masked = _should_mask_title(path, decision)
    extension = path.suffix.lower() or "[sem extensão]"

    return {
        "id": f"help-{ordinal:04d}",
        "title": f"Arquivo protegido {ordinal:04d}" if masked else _clean_title(path),
        "source": "Help.zip",
        "system": _system(path),
        "category": _category(path),
        "extension": extension,
        "size_bytes": max(info.file_size, 0),
        "status": decision.status,
        "status_label": STATUS_LABELS[decision.status],
        "reason_label": REASON_LABELS.get(decision.reason, decision.reason),
        "masked_title": masked,
    }


def catalog_zip(archive_path) -> dict[str, object]:
    items: list[dict[str, object]] = []
    decisions: Counter[str] = Counter()

    with ZipFile(archive_path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            item = _source_item(info, len(items) + 1)
            items.append(item)
            decisions[str(item["status"])] += 1

    items.extend([
        {
            "id": "bdc-small-commerce",
            "title": "BDC Small Commerce",
            "source": "Base externa",
            "system": "Small Commerce",
            "category": "Base de conhecimento",
            "extension": "web",
            "size_bytes": 0,
            "status": "external",
            "status_label": "Link oficial cadastrado",
            "reason_label": "Sincronização automática aguarda autorização formal",
            "masked_title": False,
            "url": "https://bdc.smallsoft.com.br/",
        },
        {
            "id": "bdc-zweb",
            "title": "BDC ZWeb",
            "source": "Base externa",
            "system": "ZWeb",
            "category": "Base de conhecimento",
            "extension": "web",
            "size_bytes": 0,
            "status": "external",
            "status_label": "Link oficial cadastrado",
            "reason_label": "Sincronização automática aguarda autorização formal",
            "masked_title": False,
            "url": "https://bdc.zweb.com.br/",
        },
    ])

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "archive_name": archive_path.name,
        "archive_files": len(items) - 2,
        "external_sources": 2,
        "total_sources": len(items),
        "by_decision": dict(sorted(decisions.items())),
        "privacy": "Only reviewed metadata is included; protected filenames and file contents are omitted.",
        "items": items,
    }
