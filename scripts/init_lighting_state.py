#!/usr/bin/env python3
"""Inicializa, uma única vez, o estado das quatro tomadas homologadas."""

from __future__ import annotations

import argparse
from datetime import time
from pathlib import Path

from hub.growhub.domain.remote_lighting import RemoteLightSchedule
from hub.growhub.services.lighting_store import FileLightingStore


def initialize(path: Path, entities: list[str]) -> None:
    if path.exists():
        raise FileExistsError("estado já existe; inicialização não sobrescreve dados")
    if len(entities) != 4 or len(set(entities)) != 4:
        raise ValueError("informe exatamente quatro entidades switch únicas")
    schedules = tuple(
        RemoteLightSchedule(
            entity_id=entity_id,
            on_time=time(18),
            off_time=time(6),
            weekdays=frozenset(range(7)),
            enabled=False,
        )
        for entity_id in entities
    )
    FileLightingStore(path).save(schedules, {})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria agendas desativadas para quatro tomadas EKAZA."
    )
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--entity", required=True, action="append")
    args = parser.parse_args()
    initialize(args.state, args.entity)
    print(
        "Estado inicial criado com agendas desativadas; desativada significa "
        "estado desejado OFF. Revise os horários antes de iniciar o serviço."
    )


if __name__ == "__main__":
    main()
