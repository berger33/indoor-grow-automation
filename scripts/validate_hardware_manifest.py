#!/usr/bin/env python3
"""Valida BOM, pinagem e mapa de atuadores da montagem DIY."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware" / "controller-rev-a"
SYSTEM_HARDWARE = ROOT / "hardware" / "system"
REFERENCE_RANGE = re.compile(r"^([A-Z]+)(\d+)(?:-([A-Z]+)(\d+))?$")
VALID_STATUS = {"PLANEJADO", "VALIDAR", "REUTILIZAR", "OPCIONAL"}
FORBIDDEN_ACTIVE_HARDWARE = {
    "SN74HCT595",
    "MCP23017",
    "ATLAS EZO",
    "GERBER",
    "KICAD",
}


@dataclass(frozen=True, slots=True)
class ManifestResult:
    errors: tuple[str, ...]
    pending_validation: tuple[str, ...]
    references: frozenset[str]
    total_brl: Decimal


def expand_reference_group(value: str) -> tuple[str, ...]:
    """Expande `R1-R8`; referências não numéricas permanecem literais."""
    match = REFERENCE_RANGE.fullmatch(value)
    if not match:
        return (value,)
    start_prefix, start_text, end_prefix, end_text = match.groups()
    if end_prefix is None:
        return (value,)
    if start_prefix != end_prefix:
        raise ValueError(f"prefixos incompatíveis em {value}")
    start, end = int(start_text), int(end_text)
    if end < start:
        raise ValueError(f"intervalo invertido em {value}")
    return tuple(f"{start_prefix}{number}" for number in range(start, end + 1))


def expand_reference_expression(value: str) -> tuple[str, ...]:
    references: list[str] = []
    for group in value.split(","):
        clean = group.strip()
        if clean:
            references.extend(expand_reference_group(clean))
    return tuple(references)


def load_csv(directory: Path, name: str) -> list[dict[str, str]]:
    with (directory / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def expected_output_channels(count: int) -> tuple[str, ...]:
    if count < 1:
        raise ValueError("quantidade de saídas deve ser positiva")
    return tuple(f"OUT{number:02d}" for number in range(1, count + 1))


def validate_actuator_rows(
    rows: list[dict[str, str]], expected_count: int
) -> tuple[str, ...]:
    errors: list[str] = []
    expected = expected_output_channels(expected_count)
    channels = tuple(row.get("channel", "") for row in rows)
    if channels != expected:
        errors.append(
            "actuator-map: canais devem ser exatamente " + ",".join(expected)
        )
    functions = [row.get("function", "") for row in rows]
    duplicates = sorted({name for name in functions if functions.count(name) > 1})
    if duplicates:
        errors.append("actuator-map: funções duplicadas: " + ",".join(duplicates))
    for line_number, row in enumerate(rows, start=2):
        if not row.get("safe_state"):
            errors.append(f"actuator-map:{line_number}: safe_state ausente")
        if row.get("safe_state") != "OFF":
            errors.append(f"actuator-map:{line_number}: estado seguro deve ser OFF")
        if not row.get("interlock"):
            errors.append(f"actuator-map:{line_number}: interlock ausente")
    return tuple(errors)


def validate_manifests() -> ManifestResult:
    errors: list[str] = []
    pending: list[str] = []
    references: set[str] = set()
    total = Decimal("0")

    bom = load_csv(HARDWARE, "BOM.csv")
    required_columns = {
        "item",
        "refs",
        "qty",
        "status",
        "unit_price_brl",
        "subtotal_brl",
        "verification",
    }
    if not bom or not required_columns.issubset(bom[0]):
        errors.append("BOM: colunas obrigatórias ausentes")

    for line_number, row in enumerate(bom, start=2):
        item = row.get("item", "")
        status = row.get("status", "")
        if status not in VALID_STATUS:
            errors.append(f"BOM:{line_number}: status inválido em {item}")
        if status == "VALIDAR":
            pending.append(item)
        if not row.get("verification"):
            errors.append(f"BOM:{line_number}: verificação ausente em {item}")
        try:
            quantity = int(row.get("qty", ""))
            unit_price = Decimal(row.get("unit_price_brl", ""))
            subtotal = Decimal(row.get("subtotal_brl", ""))
        except (ValueError, InvalidOperation):
            errors.append(f"BOM:{line_number}: quantidade/preço inválido em {item}")
            continue
        if quantity < 1 or unit_price < 0 or subtotal != unit_price * quantity:
            errors.append(f"BOM:{line_number}: subtotal incoerente em {item}")
        total += subtotal
        try:
            expanded = expand_reference_expression(row.get("refs", ""))
        except ValueError as exc:
            errors.append(f"BOM:{line_number}: {exc}")
            continue
        numeric_range = all(
            REFERENCE_RANGE.fullmatch(ref) for ref in row.get("refs", "").split(",")
        )
        if numeric_range and len(expanded) != quantity:
            errors.append(
                f"BOM:{line_number}: {item} declara qty={quantity}, refs={len(expanded)}"
            )
        for reference in expanded:
            if reference in references:
                errors.append(f"BOM:{line_number}: referência duplicada {reference}")
            references.add(reference)

    if not Decimal("1000") <= total <= Decimal("1650"):
        errors.append(f"BOM: total R$ {total} fora da faixa R$ 1.000–1.650")

    io_rows = load_csv(HARDWARE, "io-map.csv")
    io_text = " ".join(value for row in io_rows for value in row.values()).upper()
    for forbidden in FORBIDDEN_ACTIVE_HARDWARE:
        if forbidden in io_text:
            errors.append(f"io-map: hardware pesado ativo encontrado: {forbidden}")
    output_rows = [
        row
        for row in io_rows
        if row.get("source") == "ESP32" and row.get("boot_state") == "OFF"
    ]
    if len(output_rows) != 12:
        errors.append("io-map: deve haver exatamente 12 saídas GPIO em OFF no boot")
    pins = [row.get("pin_or_address", "") for row in io_rows if row.get("source") == "ESP32"]
    duplicates = sorted({pin for pin in pins if pins.count(pin) > 1})
    if duplicates:
        errors.append("io-map: GPIO duplicado: " + ",".join(duplicates))
    for function in ("PH_ANALOG", "EC_ANALOG", "LEAK", "LOCAL_STOP"):
        if not any(row.get("function") == function for row in io_rows):
            errors.append(f"io-map: função obrigatória ausente: {function}")

    actuator_rows = load_csv(SYSTEM_HARDWARE, "actuator-map.csv")
    errors.extend(validate_actuator_rows(actuator_rows, 12))

    return ManifestResult(
        tuple(errors), tuple(pending), frozenset(references), total
    )


def main() -> int:
    result = validate_manifests()
    for item in result.pending_validation:
        print(f"[hardware] VALIDAR: {item}")
    for error in result.errors:
        print(f"[hardware] ERRO: {error}")
    if result.errors:
        print(f"[hardware] reprovado: {len(result.errors)} erro(s)")
        return 1
    print(
        f"[hardware] DIY coerente: {len(result.references)} referências; "
        f"total R$ {result.total_brl}; "
        f"{len(result.pending_validation)} item(ns) para bancada"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
