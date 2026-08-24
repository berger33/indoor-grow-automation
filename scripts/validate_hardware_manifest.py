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


def validate_layout_contract(contract: dict[str, object]) -> tuple[str, ...]:
    """Impede regressão para tanques lado a lado ou apoios compartilhados."""
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("layout-contract: schema_version deve ser 1")
    if contract.get("lighting_hardware_included") is not False:
        errors.append("layout-contract: hardware de iluminação deve permanecer ausente")
    if contract.get("lighting_software_integration") != "ekaza_tuya_via_hub":
        errors.append("layout-contract: integração de luz deve ocorrer somente pelo hub")
    if contract.get("arrangement") != "vertical_stacked":
        errors.append("layout-contract: arrangement deve ser vertical_stacked")

    envelope = contract.get("rack_envelope_max_mm")
    expected_envelope = {"width": 900, "depth": 600, "height": 2000}
    if envelope != expected_envelope:
        errors.append("layout-contract: envelope máximo deve ser 900x600x2000 mm")

    tanks = contract.get("tanks")
    if not isinstance(tanks, list) or len(tanks) != 2:
        errors.append("layout-contract: devem existir exatamente dois tanques")
        return tuple(errors)
    expected = {
        "TK-101": ("source_water", "upper"),
        "TK-201": ("mix_irrigation", "lower"),
    }
    platforms: set[object] = set()
    shelves: set[object] = set()
    for tank in tanks:
        if not isinstance(tank, dict):
            errors.append("layout-contract: tanque deve ser objeto")
            continue
        tank_id = tank.get("id")
        if tank_id not in expected:
            errors.append(f"layout-contract: tanque inesperado {tank_id}")
            continue
        role, tier = expected[str(tank_id)]
        if (tank.get("role"), tank.get("tier")) != (role, tier):
            errors.append(f"layout-contract: função/nível inválido em {tank_id}")
        if tank.get("nominal_volume_l") != 50:
            errors.append(f"layout-contract: {tank_id} deve ter 50 L nominais")
        platforms.add(tank.get("platform"))
        shelves.add(tank.get("shelf"))
    if None in platforms or len(platforms) != 2:
        errors.append("layout-contract: plataformas devem ser independentes")
    if None in shelves or len(shelves) != 2:
        errors.append("layout-contract: prateleiras devem ser independentes")

    containment = contract.get("containment")
    if not isinstance(containment, dict):
        errors.append("layout-contract: contenção ausente")
    else:
        if containment.get("upper_collector") != "CT2":
            errors.append("layout-contract: coletor superior deve ser CT2")
        if containment.get("upper_drain_count") != 2:
            errors.append("layout-contract: CT2 deve ter dois drenos")
        if containment.get("drains_to") != containment.get("base"):
            errors.append("layout-contract: CT2 deve drenar para a contenção-base")
        if containment.get("base") != "CT1":
            errors.append("layout-contract: contenção-base deve ser CT1")
        if containment.get("base_free_volume_l") != 110:
            errors.append("layout-contract: CT1 deve declarar 110 L livres")
    return tuple(errors)


def validate_stirrer_contract(
    contract: dict[str, object], references: set[str] | frozenset[str]
) -> tuple[str, ...]:
    """Valida quantidade, identidade, energia e feedback da dosagem de referência."""
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("stirrer-contract: schema_version deve ser 1")
    if contract.get("release_state") != "HOLD":
        errors.append("stirrer-contract: revisão A0 deve permanecer em HOLD")
    if contract.get("channel_count") != 6:
        errors.append("stirrer-contract: devem existir exatamente seis canais")

    channels = contract.get("channels")
    expected_names = ["ph_down", "calmag", "micro", "bloom", "veg", "ph_up"]
    if not isinstance(channels, list) or len(channels) != 6:
        errors.append("stirrer-contract: lista de canais deve conter seis itens")
    else:
        names = [channel.get("name") for channel in channels if isinstance(channel, dict)]
        indices = [channel.get("index") for channel in channels if isinstance(channel, dict)]
        tachs = [channel.get("tach") for channel in channels if isinstance(channel, dict)]
        if names != expected_names:
            errors.append("stirrer-contract: ordem química divergente da referência")
        if indices != list(range(6)):
            errors.append("stirrer-contract: índices devem ser 0..5")
        if len(set(tachs)) != 6:
            errors.append("stirrer-contract: cada canal deve ter tacômetro exclusivo")
        for channel in channels:
            if not isinstance(channel, dict):
                continue
            for field in ("pump", "stirrer"):
                reference = channel.get(field)
                if reference not in references:
                    errors.append(
                        f"stirrer-contract: referência {reference} ausente da BOM"
                    )

    drive = contract.get("drive")
    if not isinstance(drive, dict):
        errors.append("stirrer-contract: acionamento ausente")
    else:
        expected_drive = {
            "enable_output": "OUT07",
            "supply_vdc": 12,
            "mode": "grouped_full_speed",
            "converter": "DC2",
            "branch_fusing_required": True,
        }
        for key, expected in expected_drive.items():
            if drive.get(key) != expected:
                errors.append(f"stirrer-contract: {key} deve ser {expected}")
        if drive.get("converter") not in references:
            errors.append("stirrer-contract: conversor DC2 ausente da BOM")

    mechanics = contract.get("mechanics")
    if not isinstance(mechanics, dict):
        errors.append("stirrer-contract: mecânica ausente")
    else:
        if mechanics.get("magnets_per_fan") != 2:
            errors.append("stirrer-contract: cada ventilador deve usar dois ímãs")
        if mechanics.get("magnet_retention_guard_required") is not True:
            errors.append("stirrer-contract: proteção de retenção é obrigatória")
        if mechanics.get("stir_bar_coating") != "PTFE":
            errors.append("stirrer-contract: barra deve ser revestida em PTFE")

    feedback = contract.get("feedback")
    if not isinstance(feedback, dict) or any(
        feedback.get(key) is not True
        for key in ("required_before_dosing", "required_during_dosing")
    ):
        errors.append("stirrer-contract: rotação deve intertravar toda dosagem")

    sequence = contract.get("reference_sequence")
    if not isinstance(sequence, dict):
        errors.append("stirrer-contract: sequência de referência ausente")
    else:
        if sequence.get("nutrient_order") != ["calmag", "micro", "bloom", "veg"]:
            errors.append("stirrer-contract: ordem deve ser CalMag/Micro/Bloom/Veg")
        if sequence.get("settling_between_nutrients_seconds") != 60:
            errors.append("stirrer-contract: intervalo entre nutrientes deve ser 60 s")
        if set(sequence.get("ph_channels_excluded_from_batch_recipe", [])) != {
            "ph_down",
            "ph_up",
        }:
            errors.append("stirrer-contract: pH Up/Down não pertencem à receita base")
    return tuple(errors)


def validate_exhaust_contract(
    contract: dict[str, object], references: set[str] | frozenset[str]
) -> tuple[str, ...]:
    """Mantém a transição do exaustor reversível e sem presumir pinagem."""
    errors: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("exhaust-contract: schema_version deve ser 1")
    if contract.get("release_state") != "HOLD":
        errors.append("exhaust-contract: interface direta deve permanecer em HOLD")
    installed = contract.get("installed_profile")
    if not isinstance(installed, dict) or installed.get("control_mode") != "contactor_on_off_only":
        errors.append("exhaust-contract: exaustor atual deve ser somente liga/desliga")
    target = contract.get("target_profile")
    if not isinstance(target, dict):
        errors.append("exhaust-contract: perfil alvo ausente")
    else:
        if (target.get("mpn"), target.get("duct_in"), target.get("airflow_cfm")) != (
            "AI-CLS6",
            6,
            402,
        ):
            errors.append("exhaust-contract: alvo deve ser AI-CLS6 de 6 pol/402 CFM")
        if target.get("direct_control_state") != "HOLD_UNTIL_EXACT_REVISION_PINOUT":
            errors.append("exhaust-contract: pinagem direta não pode estar liberada")
    requirements = contract.get("control_requirements")
    required_true = (
        "local_fallback_required",
        "loss_of_esp32_must_not_stop_required_ventilation",
        "anti_cycle_required",
        "command_feedback_separation_required",
        "absolute_temperature_and_humidity_limits_override_vpd",
    )
    if not isinstance(requirements, dict) or any(
        requirements.get(key) is not True for key in required_true
    ):
        errors.append("exhaust-contract: requisitos fail-safe incompletos")
    if not {"FAN1", "IF-F1"}.issubset(references):
        errors.append("exhaust-contract: FAN1 e IF-F1 devem constar na BOM")
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
    with (SYSTEM_HARDWARE / "layout-contract.json").open(encoding="utf-8") as handle:
        errors.extend(validate_layout_contract(json.load(handle)))
    with (SYSTEM_HARDWARE / "stirrer-contract.json").open(encoding="utf-8") as handle:
        errors.extend(validate_stirrer_contract(json.load(handle), references))
    with (SYSTEM_HARDWARE / "exhaust-contract.json").open(encoding="utf-8") as handle:
        errors.extend(validate_exhaust_contract(json.load(handle), references))
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
