#!/usr/bin/env python3
"""Executa o portão de qualidade reproduzível do repositório."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> None:
    """Executa um comando no repositório e encerra no primeiro erro."""
    print(f"[quality] {label}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def existing_python_roots() -> list[str]:
    """Retorna apenas árvores Python existentes na fase atual."""
    return [name for name in ("hub", "tests", "scripts") if (ROOT / name).exists()]


def main() -> int:
    run("whitespace", ["git", "diff", "--check", "HEAD"])

    roots = existing_python_roots()
    if roots:
        run("python compile", [sys.executable, "-m", "compileall", "-q", *roots])

    if (ROOT / "tests").exists():
        run(
            "unit tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        )

    hardware_validator = ROOT / "scripts" / "validate_hardware_manifest.py"
    if hardware_validator.exists():
        run("hardware manifests", [sys.executable, str(hardware_validator)])

    secret_scanner = ROOT / "scripts" / "secret_scan.py"
    if secret_scanner.exists():
        run("secret scan", [sys.executable, str(secret_scanner), "--tracked"])

    print("[quality] aprovado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
