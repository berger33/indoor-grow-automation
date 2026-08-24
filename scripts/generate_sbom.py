#!/usr/bin/env python3
"""Gera SBOM SPDX 2.3 determinística a partir dos manifests versionados."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "sbom/indoor-grow.spdx.json"
PYTHON_LICENSES = {
    "fastapi": "MIT",
    "uvicorn": "BSD-3-Clause",
    "sqlalchemy": "MIT",
    "alembic": "MIT",
    "psycopg": "LGPL-3.0-only",
    "paho-mqtt": "EPL-2.0 OR BSD-3-Clause",
}
FIRMWARE_LICENSES = {
    "platformio/platform-espressif32": "Apache-2.0",
    "adafruit/Adafruit_BME280_Library": "BSD-3-Clause",
    "adafruit/Adafruit-MLX90614-Library": "BSD-3-Clause",
    "PaulStoffregen/OneWire": "NOASSERTION",
    "milesburton/Arduino-Temperature-Control-Library": "MIT",
    "bogde/HX711": "MIT",
}


def spdx_id(ecosystem: str, name: str, version: str) -> str:
    digest = hashlib.sha256(f"{ecosystem}:{name}:{version}".encode()).hexdigest()[:16]
    return f"SPDXRef-Package-{ecosystem}-{digest}"


def package(ecosystem: str, name: str, version: str, license_id: str, location: str, purl: str) -> dict[str, object]:
    return {
        "SPDXID": spdx_id(ecosystem, name, version),
        "name": name,
        "versionInfo": version,
        "downloadLocation": location,
        "filesAnalyzed": False,
        "licenseConcluded": license_id,
        "licenseDeclared": license_id,
        "copyrightText": "NOASSERTION",
        "externalRefs": [{"referenceCategory": "PACKAGE-MANAGER", "referenceType": "purl", "referenceLocator": purl}],
        "supplier": "NOASSERTION",
    }


def python_packages() -> list[dict[str, object]]:
    result = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        name, version = line.split("==", maxsplit=1)
        normalized = name.split("[", maxsplit=1)[0].lower()
        result.append(package("pypi", name, version, PYTHON_LICENSES[normalized], "NOASSERTION", f"pkg:pypi/{quote(normalized)}@{quote(version)}"))
    return result


def npm_packages() -> list[dict[str, object]]:
    lock = json.loads((ROOT / "web/package-lock.json").read_text(encoding="utf-8"))
    result = []
    for path, value in sorted(lock["packages"].items()):
        if not path or "version" not in value:
            continue
        name = path.removeprefix("node_modules/")
        version = value["version"]
        result.append(package("npm", name, version, value.get("license", "NOASSERTION"), value.get("resolved", "NOASSERTION"), f"pkg:npm/{quote(name, safe='')}@{quote(version)}"))
    return result


def firmware_packages() -> list[dict[str, object]]:
    urls: set[str] = set()
    for ini in (ROOT / "firmware").glob("*/platformio.ini"):
        urls.update(re.findall(r"https://github\.com/[^\s]+#[0-9a-f]{40}", ini.read_text(encoding="utf-8")))
    result = []
    for url in sorted(urls):
        repository, commit = url.rsplit("#", maxsplit=1)
        identity = repository.removeprefix("https://github.com/").removesuffix(".git")
        result.append(package("github", identity, commit, FIRMWARE_LICENSES.get(identity, "NOASSERTION"), repository, f"pkg:github/{identity}@{commit}"))
    result.append(package("vendored", "platformio/platform-native", "1.2.1+7df81639bc84474e9b1812d241762cffad9c69e7", "Apache-2.0", "https://github.com/platformio/platform-native", "pkg:github/platformio/platform-native@7df81639bc84474e9b1812d241762cffad9c69e7"))
    return result


def document() -> dict[str, object]:
    packages = sorted((*python_packages(), *npm_packages(), *firmware_packages()), key=lambda item: str(item["SPDXID"]))
    root = "SPDXRef-Package-indoor-grow-automation"
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "indoor-grow-automation-sbom",
        "documentNamespace": "https://indoor-grow.local/sbom/v1/2026-08-24",
        "creationInfo": {"created": "2026-08-24T00:00:00Z", "creators": ["Tool: scripts/generate_sbom.py"]},
        "documentDescribes": [root],
        "packages": [{
            "SPDXID": root,
            "name": "indoor-grow-automation",
            "versionInfo": "1.0.0-a0",
            "downloadLocation": "https://github.com/berger33/indoor-grow-automation",
            "filesAnalyzed": False,
            "licenseConcluded": "MIT",
            "licenseDeclared": "MIT",
            "copyrightText": "Copyright (c) 2026 Indoor Grow Automation contributors",
            "supplier": "Organization: Indoor Grow Automation contributors",
        }, *packages],
        "relationships": [{"spdxElementId": root, "relationshipType": "DEPENDS_ON", "relatedSpdxElement": item["SPDXID"]} for item in packages],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(document(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print("[sbom] desatualizada; execute scripts/generate_sbom.py")
            return 1
        print("[sbom] SPDX sincronizada")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"[sbom] {len(document()['packages']) - 1} dependências registradas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
