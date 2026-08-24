"""Composição de produção do hub a partir de configuração de ambiente."""

from __future__ import annotations

import os
from datetime import time
from pathlib import Path

from .app import create_app
from ..domain.remote_lighting import RemoteLightSchedule
from ..integrations.home_assistant import HomeAssistantSwitchClient
from ..persistence.database import create_database_engine, create_session_factory
from ..persistence.lighting import SqlLightingStore
from ..services.lighting_application import LightingApplicationService


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"variável obrigatória ausente: {name}")
    return value


def build_runtime_app():
    """Cria API, worker de reconciliação e painel sem persistir credenciais."""
    sessions = create_session_factory(create_database_engine(_required_env("GROWHUB_DATABASE_URL")))
    store = SqlLightingStore(sessions)
    if store.is_empty():
        entities = tuple(
            item.strip()
            for item in os.environ.get("GROWHUB_EKAZA_ENTITIES", "").split(",")
            if item.strip()
        )
        if len(entities) != 4 or len(set(entities)) != 4:
            raise RuntimeError(
                "banco EKAZA vazio: configure exatamente quatro GROWHUB_EKAZA_ENTITIES"
            )
        store.save(
            tuple(
                RemoteLightSchedule(
                    entity_id=entity_id,
                    on_time=time(18),
                    off_time=time(6),
                    weekdays=frozenset(range(7)),
                    enabled=False,
                )
                for entity_id in entities
            ),
            {},
        )
    store.load()
    client = HomeAssistantSwitchClient(
        base_url=_required_env("GROWHUB_HA_URL"),
        access_token=_required_env("GROWHUB_HA_TOKEN"),
    )
    service = LightingApplicationService(store, client=client)
    default_dist = Path(__file__).resolve().parents[3] / "web" / "dist"
    web_dist = Path(os.environ.get("GROWHUB_WEB_DIST", default_dist))
    return create_app(service, web_dist=web_dist)
