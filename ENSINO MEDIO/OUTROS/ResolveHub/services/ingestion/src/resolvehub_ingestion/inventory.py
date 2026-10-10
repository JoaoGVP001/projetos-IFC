from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from .policy import classify_entry


def _is_symlink(info: ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return (mode & 0o170000) == 0o120000


def inventory_zip(archive_path: Path) -> dict[str, object]:
    decisions: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    extensions: Counter[str] = Counter()
    total_files = 0
    total_uncompressed_bytes = 0

    with ZipFile(archive_path) as archive:
        for info in archive.infolist():
            decision = classify_entry(
                info.filename,
                info.file_size,
                is_directory=info.is_dir(),
                is_symlink=_is_symlink(info),
            )
            if info.is_dir():
                continue

            total_files += 1
            total_uncompressed_bytes += max(info.file_size, 0)
            decisions[decision.status] += 1
            reasons[decision.reason] += 1
            extensions[decision.extension or "[no-extension]"] += 1

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "archive_name": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "total_files": total_files,
        "total_uncompressed_bytes": total_uncompressed_bytes,
        "by_decision": dict(sorted(decisions.items())),
        "by_reason": dict(sorted(reasons.items())),
        "by_extension": dict(sorted(extensions.items())),
        "privacy": "Aggregate counts only; filenames and contents are intentionally omitted.",
    }
