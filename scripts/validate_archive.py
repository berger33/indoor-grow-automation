#!/usr/bin/env python3
"""Confirma que a engenharia pesada ficou fora dos caminhos ativos."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "engenharia-pesada"


def archive_errors() -> tuple[str, ...]:
    errors: list[str] = []
    required = (
        ARCHIVE / "README.md",
        ARCHIVE / "desenhos",
        ARCHIVE / "hardware" / "controller-rev-a" / "netlist.csv",
        ARCHIVE / "hardware" / "controller-rev-a" / "pcb-parameters.json",
        ARCHIVE / "firmware" / "nos-distribuidos",
    )
    for path in required:
        if not path.exists():
            errors.append(f"arquivo histórico ausente: {path.relative_to(ROOT)}")

    forbidden_active = (
        ROOT / "desenhos",
        ROOT / "hardware" / "controller-rev-a" / "netlist.csv",
        ROOT / "hardware" / "controller-rev-a" / "pcb-parameters.json",
        ROOT / "firmware" / "fertigation",
        ROOT / "firmware" / "climate",
        ROOT / "firmware" / "safety",
        ROOT / "docs" / "RASPBERRY_PI_OPERACAO.md",
    )
    for path in forbidden_active:
        if path.exists():
            errors.append(f"engenharia pesada ainda ativa: {path.relative_to(ROOT)}")
    return tuple(errors)


def main() -> int:
    errors = archive_errors()
    for error in errors:
        print(f"[archive] ERRO: {error}")
    if errors:
        return 1
    print("[archive] engenharia pesada preservada somente no arquivo histórico")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
