from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}
REVIEW_EXTENSIONS = {".sql", ".yml", ".yaml", ".csv", ".rtf"}
DEFERRED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".mp4"}
BLOCKED_EXTENSIONS = {
    ".pfx", ".p12", ".pem", ".key", ".kdb", ".fdb", ".db", ".sqlite", ".sqlite3",
    ".exe", ".dll", ".sys", ".inf", ".cat", ".msi", ".bat", ".cmd", ".ps1", ".vbs",
    ".reg", ".apk", ".rar", ".7z", ".zip", ".tar", ".gz",
}
SECRET_NAME_PATTERN = re.compile(r"(^|[\s._-])(senhas?|passwords?|credentials?|secrets?|tokens?|api[_-]?keys?)([\s._-]|$)", re.IGNORECASE)
PII_NAME_PATTERN = re.compile(r"(^|[\s._-])(cpf|cnpj|cliente|clientes)([\s._-]|$)", re.IGNORECASE)
MAX_ENTRY_BYTES = 50 * 1024 * 1024


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str
    extension: str


def _safe_archive_path(name: str) -> PurePosixPath | None:
    normalized = name.replace("\\", "/")
    if not normalized or "\x00" in normalized or re.match(r"^[a-zA-Z]:", normalized):
        return None

    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path


def classify_entry(name: str, size: int, *, is_directory: bool = False, is_symlink: bool = False) -> Decision:
    if is_directory:
        return Decision("skip", "directory", "")

    path = _safe_archive_path(name)
    if path is None:
        return Decision("block", "unsafe_path", "")

    extension = path.suffix.lower()
    basename = path.name
    full_path = " ".join(path.parts)

    if is_symlink:
        return Decision("block", "symlink", extension)
    if size < 0 or size > MAX_ENTRY_BYTES:
        return Decision("block", "size_limit", extension)
    if extension in BLOCKED_EXTENSIONS:
        return Decision("block", "blocked_extension", extension)
    if SECRET_NAME_PATTERN.search(full_path):
        return Decision("block", "secret_filename", extension)
    if extension in REVIEW_EXTENSIONS or PII_NAME_PATTERN.search(full_path):
        return Decision("review", "manual_review", extension)
    if extension in SUPPORTED_EXTENSIONS:
        return Decision("include", "supported_document", extension)
    if extension in DEFERRED_EXTENSIONS:
        return Decision("defer", "future_ocr_or_media", extension)
    return Decision("skip", "unsupported_extension", extension or "[no-extension]")
