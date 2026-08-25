#!/usr/bin/env python3
"""Valida integridade mínima das pranchas SVG Rev A."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "http://www.w3.org/2000/svg"


def validate_drawing(path: Path) -> None:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise ValueError(f"{path.name}: XML inválido") from exc
    root = tree.getroot()
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ValueError(f"{path.name}: raiz SVG inválida")
    if not root.get("viewBox"):
        raise ValueError(f"{path.name}: viewBox ausente")
    text = " ".join(node.text or "" for node in root.iter())
    if "HOLD" not in text:
        raise ValueError(f"{path.name}: status HOLD ausente")
    for node in root.iter():
        for attribute, value in node.attrib.items():
            if attribute.endswith("href") and value.startswith(("http:", "https:", "data:")):
                raise ValueError(f"{path.name}: recurso externo incorporado")


def validate_drawings(directory: Path) -> int:
    drawings = sorted(directory.glob("REV-A-*.svg"))
    if not drawings:
        raise ValueError("nenhuma prancha Rev A encontrada")
    for path in drawings:
        validate_drawing(path)
    return len(drawings)


def main() -> int:
    try:
        count = validate_drawings(ROOT / "desenhos")
    except ValueError as exc:
        print(f"[drawings] erro: {exc}", file=sys.stderr)
        return 1
    print(f"[drawings] {count} pranchas Rev A válidas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())