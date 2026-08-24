#!/usr/bin/env python3
"""Valida os PNGs documentais sem depender de codecs do sistema operacional."""

from __future__ import annotations

import binascii
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
TEXT_SUFFIXES = {".md", ".py", ".json", ".csv", ".yml", ".yaml", ".svg"}
OBSOLETE_SUFFIX = "." + "webp"


def validate_png(
    path: Path,
    *,
    minimum_width: int = 1,
    minimum_height: int = 1,
) -> tuple[int, int]:
    """Verifica assinatura, chunks, CRC e conteúdo de um PNG RGB/RGBA de 8 bits."""
    data = path.read_bytes()
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError(f"{path.name}: arquivo excede 10 MiB")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path.name}: assinatura PNG inválida")

    offset = len(PNG_SIGNATURE)
    width = height = channels = 0
    compressed = bytearray()
    seen_ihdr = False
    seen_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f"{path.name}: chunk PNG truncado")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise ValueError(f"{path.name}: dados de chunk truncados")
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        actual_crc = binascii.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"{path.name}: CRC inválido em {chunk_type!r}")

        if chunk_type == b"IHDR":
            if seen_ihdr or offset != len(PNG_SIGNATURE) or length != 13:
                raise ValueError(f"{path.name}: IHDR inválido")
            width, height, bit_depth, color_type, compression, filtering, interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            if bit_depth != 8 or color_type not in {0, 2, 6}:
                raise ValueError(f"{path.name}: formato deve ser PNG de 8 bits")
            if compression != 0 or filtering != 0 or interlace != 0:
                raise ValueError(f"{path.name}: codificação PNG não suportada")
            channels = {0: 1, 2: 3, 6: 4}[color_type]
            seen_ihdr = True
        elif chunk_type == b"IDAT":
            if not seen_ihdr or seen_iend:
                raise ValueError(f"{path.name}: IDAT fora de ordem")
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            if length or not seen_ihdr:
                raise ValueError(f"{path.name}: IEND inválido")
            seen_iend = True
            if chunk_end != len(data):
                raise ValueError(f"{path.name}: bytes após IEND")
        offset = chunk_end

    if not seen_ihdr or not seen_iend or not compressed:
        raise ValueError(f"{path.name}: estrutura PNG incompleta")
    if width < minimum_width or height < minimum_height:
        raise ValueError(f"{path.name}: resolução abaixo do mínimo")
    if width > 4096 or height > 4096:
        raise ValueError(f"{path.name}: resolução acima de 4096 px")

    try:
        pixels = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise ValueError(f"{path.name}: pixels PNG não decodificam") from exc
    row_bytes = width * channels
    expected = height * (row_bytes + 1)
    if len(pixels) != expected:
        raise ValueError(f"{path.name}: tamanho de pixels incoerente")
    for row in range(height):
        if pixels[row * (row_bytes + 1)] > 4:
            raise ValueError(f"{path.name}: filtro de linha PNG inválido")
    return width, height


def validate_repository_images(root: Path = ROOT) -> tuple[Path, ...]:
    directory = root / "docs" / "images" / "realistic"
    images = tuple(sorted(directory.glob("*.png")))
    if len(images) < 3:
        raise ValueError("imagens realistas: mínimo de três PNGs")
    unexpected = sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() not in {".png", ".md"}
    )
    if unexpected:
        raise ValueError("imagens realistas: formatos proibidos: " + ", ".join(unexpected))
    for path in images:
        validate_png(path, minimum_width=1024, minimum_height=600)

    stale_references: list[str] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if OBSOLETE_SUFFIX in path.read_text(encoding="utf-8", errors="ignore").lower():
            stale_references.append(str(path.relative_to(root)))
    if stale_references:
        raise ValueError("referências WebP obsoletas: " + ", ".join(stale_references))
    return images


def main() -> int:
    try:
        images = validate_repository_images()
    except ValueError as exc:
        print(f"[images] erro: {exc}", file=sys.stderr)
        return 1
    print(f"[images] {len(images)} PNGs íntegros e decodificáveis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
