from __future__ import annotations

import argparse
import json
from pathlib import Path

from .inventory import inventory_zip


def _inventory(args: argparse.Namespace) -> int:
    archive = Path(args.archive).expanduser().resolve(strict=True)
    if archive.suffix.lower() != ".zip":
        raise SystemExit("O inventário inicial aceita somente arquivos .zip.")

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = inventory_zip(archive)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ferramentas seguras de ingestão do ResolveHub")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="Inventaria um ZIP sem extrair arquivos")
    inventory.add_argument("--archive", required=True, help="Caminho do arquivo ZIP")
    inventory.add_argument("--output", required=True, help="Caminho do resumo JSON agregado")
    inventory.set_defaults(handler=_inventory)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
