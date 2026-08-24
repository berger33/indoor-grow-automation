#!/usr/bin/env python3
"""Executa o portão de qualidade reproduzível do repositório."""

from __future__ import annotations

import os
import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("PLATFORMIO_CORE_DIR", str(ROOT / ".platformio-core"))
os.environ.setdefault("PLATFORMIO_SETTING_ENABLE_TELEMETRY", "no")


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

    hil_project = ROOT / "firmware" / "hil" / "platformio.ini"
    if hil_project.exists():
        if os.environ.get("CI") == "true":
            pio = shutil.which("pio")
            if pio is None:
                raise SystemExit("PlatformIO ausente no CI")
            run("firmware HIL PlatformIO", [pio, "run", "--project-dir", "firmware/hil"])
            executable = ROOT / "firmware" / "hil" / ".pio" / "build" / "native_hil" / "program"
        else:
            executable = Path("/tmp/indoor-grow-hil")
            run(
                "firmware HIL compiler fallback",
                [
                    "g++",
                    "-std=c++17",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-Ifirmware/shared/GrowCore/src",
                    "firmware/hil/src/main.cpp",
                    "-o",
                    str(executable),
                ],
            )
        run("firmware HIL scenarios", [str(executable)])

    if os.environ.get("CI") == "true":
        pio = shutil.which("pio")
        for project in ("fertigation", "climate", "safety"):
            manifest = ROOT / "firmware" / project / "platformio.ini"
            if manifest.exists():
                if pio is None:
                    raise SystemExit("PlatformIO ausente no CI")
                run(
                    f"firmware ESP32 {project}",
                    [pio, "run", "--project-dir", f"firmware/{project}"],
                )

    web_package = ROOT / "web" / "package.json"
    if web_package.exists():
        run(
            "panel typecheck",
            ["node", "web/node_modules/typescript/bin/tsc", "-b", "web"],
        )
        run(
            "panel build",
            ["node", "web/node_modules/vite/bin/vite.js", "build", "web"],
        )

    hardware_validator = ROOT / "scripts" / "validate_hardware_manifest.py"
    if hardware_validator.exists():
        run("hardware manifests", [sys.executable, str(hardware_validator)])

    drawing_validator = ROOT / "scripts" / "validate_drawings.py"
    if drawing_validator.exists():
        run("Rev A drawings", [sys.executable, str(drawing_validator)])

    sbom_generator = ROOT / "scripts" / "generate_sbom.py"
    if sbom_generator.exists():
        run("SBOM SPDX", [sys.executable, str(sbom_generator), "--check"])

    secret_scanner = ROOT / "scripts" / "secret_scan.py"
    if secret_scanner.exists():
        run("secret scan", [sys.executable, str(secret_scanner), "--tracked"])

    print("[quality] aprovado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
