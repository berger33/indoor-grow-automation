#!/usr/bin/env python3
"""Migra o JSON legado EKAZA para o banco; padrão seguro é apenas simular."""

from __future__ import annotations

import argparse
from pathlib import Path

from hub.growhub.persistence.database import create_database_engine, create_session_factory
from hub.growhub.persistence.lighting import SqlLightingStore
from hub.growhub.services.lighting_store import FileLightingStore


def migrate(state: Path, database_url_file: Path, *, apply: bool) -> int:
    database_url = database_url_file.read_text(encoding="utf-8").strip()
    schedules, overrides = FileLightingStore(state).load()
    target = SqlLightingStore(create_session_factory(create_database_engine(database_url)))
    if not target.is_empty():
        raise ValueError("banco já contém agendas; migração não sobrescreve dados")
    if apply:
        target.save(schedules, overrides)
    return len(schedules)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migra agendas EKAZA do JSON para PostgreSQL.")
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--database-url-file", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="grava após a simulação ter sido revisada")
    args = parser.parse_args()
    count = migrate(args.state, args.database_url_file, apply=args.apply)
    mode = "gravadas" if args.apply else "validadas em simulação; nenhuma escrita feita"
    print(f"{count} agendas {mode}")


if __name__ == "__main__":
    main()
