import binascii
import struct
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scripts.validate_raster_images import validate_png, validate_repository_images


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def valid_png(width: int = 2, height: int = 2) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = b"".join(b"\x00" + b"\x20\x40\x60" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(pixels))
        + png_chunk(b"IEND", b"")
    )


class RasterImageValidationTests(TestCase):
    def test_repository_realistic_images_decode(self) -> None:
        self.assertGreaterEqual(len(validate_repository_images()), 3)

    def test_accepts_complete_png(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            path.write_bytes(valid_png())
            self.assertEqual((2, 2), validate_png(path))

    def test_rejects_wrong_signature(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            path.write_bytes(b"not a png")
            with self.assertRaisesRegex(ValueError, "assinatura"):
                validate_png(path)

    def test_rejects_corrupted_chunk_crc(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            payload = bytearray(valid_png())
            payload[29] ^= 0x01
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "CRC"):
                validate_png(path)
