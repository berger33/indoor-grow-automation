#!/usr/bin/env python3
"""Cruza BOM, I/O, netlist e limites da controladora Rev A."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware" / "controller-rev-a"
SYSTEM_HARDWARE = ROOT / "hardware" / "system"
REFERENCE_RANGE = re.compile(r"^([A-Z]+)(\d+)(?:-([A-Z]+)(\d+))?$")
REFERENCE_IN_NET = re.compile(r"\b[A-Z]+\d+\b")
VALID_STATUS = {"APPROVED_CLASS", "APPROVED_MODEL", "PROVISIONAL", "HOLD"}


@dataclass(frozen=True, slots=True)
class ManifestResult:
    errors: tuple[str, ...]
    holds: tuple[str, ...]
    references: frozenset[str]


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


def load_csv(name: str) -> list[dict[str, str]]:
    with (HARDWARE / name).open(encoding="utf-8", newline="") as handle:
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
        if not row.get("interlock"):
            errors.append(f"actuator-map:{line_number}: interlock ausente")
    return tuple(errors)


def validate_manifests() -> ManifestResult:
    errors: list[str] = []
    holds: list[str] = []
    references: set[str] = set()

    bom = load_csv("BOM.csv")
    for line_number, row in enumerate(bom, start=2):
        item = row.get("item", "")
        status = row.get("status", "")
        if status not in VALID_STATUS:
            errors.append(f"BOM:{line_number}: status inválido em {item}")
        if status == "HOLD":
            holds.append(item)
        try:
            quantity = int(row.get("qty", ""))
        except ValueError:
            errors.append(f"BOM:{line_number}: quantidade inválida em {item}")
            continue
        try:
            expanded = expand_reference_expression(row.get("refs", ""))
        except ValueError as exc:
            errors.append(f"BOM:{line_number}: {exc}")
            continue

        numeric_range = all(REFERENCE_RANGE.fullmatch(ref) for ref in row["refs"].split(","))
        if numeric_range and len(expanded) != quantity:
            errors.append(
                f"BOM:{line_number}: {item} declara qty={quantity}, refs={len(expanded)}"
            )
        for reference in expanded:
            if reference in references:
                errors.append(f"BOM:{line_number}: referência duplicada {reference}")
            references.add(reference)

    known_prefixes = {
        match.group(1)
        for reference in references
        if (match := re.match(r"^([A-Z]+)\d+$", reference))
    }
    for filename, field in (("io-map.csv", "connector"), ("netlist.csv", "connected_refs")):
        for line_number, row in enumerate(load_csv(filename), start=2):
            for reference in REFERENCE_IN_NET.findall(row.get(field, "")):
                prefix = re.match(r"^([A-Z]+)", reference).group(1)  # type: ignore[union-attr]
                if prefix not in known_prefixes:
                    continue
                if reference not in references:
                    errors.append(
                        f"{filename}:{line_number}: referência {reference} ausente da BOM"
                    )

    with (HARDWARE / "pcb-parameters.json").open(encoding="utf-8") as handle:
        parameters = json.load(handle)
    limits = parameters["electrical_limits"]
    with (SYSTEM_HARDWARE / "actuator-map.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        actuator_rows = list(csv.DictReader(handle))
    errors.extend(
        validate_actuator_rows(actuator_rows, limits.get("output_channel_count", 0))
    )
    if limits.get("mains_allowed") is not False:
        errors.append("pcb-parameters: rede CA deve permanecer proibida")
    if limits.get("input_maximum_vdc", 999) > 30:
        errors.append("pcb-parameters: entrada excede limite SELV Rev A")
    if limits.get("output_channel_maximum_a", 999) > 1:
        errors.append("pcb-parameters: canal excede 1 A sem nova revisão")
    if limits.get("output_aggregate_maximum_a", 999) > 4:
        errors.append("pcb-parameters: agregado excede 4 A sem nova revisão")
    board_limit = limits.get("output_aggregate_maximum_a", 0)
    supply_limit = limits.get("installed_power_supply_rated_a", 999)
    concurrent_limit = limits.get("installation_concurrent_limit_a", 999)
    if not 0 < concurrent_limit <= supply_limit <= board_limit:
        errors.append("pcb-parameters: limites placa/fonte/concorrência incoerentes")

    return ManifestResult(tuple(errors), tuple(holds), frozenset(references))


def main() -> int:
    result = validate_manifests()
    for hold in result.holds:
        print(f"[hardware] HOLD: {hold}")
    for error in result.errors:
        print(f"[hardware] ERRO: {error}")
    if result.errors:
        print(f"[hardware] reprovado: {len(result.errors)} erro(s)")
        return 1
    print(
        f"[hardware] manifestos coerentes: {len(result.references)} referências; "
        f"{len(result.holds)} bloqueio(s) documentado(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
