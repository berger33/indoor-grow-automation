"""Composição de produção do hub a partir de configuração de ambiente."""

from __future__ import annotations

import os
from pathlib import Path

from .app import create_app
from ..integrations.home_assistant import HomeAssistantSwitchClient
from ..services.lighting_application import LightingApplicationService
from ..services.lighting_store import FileLightingStore


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"variável obrigatória ausente: {name}")
    return value


def build_runtime_app():
    """Cria API, worker de reconciliação e painel sem persistir credenciais."""
    store = FileLightingStore(Path(_required_env("GROWHUB_LIGHTING_STATE")))
    store.load()
    client = HomeAssistantSwitchClient(
        base_url=_required_env("GROWHUB_HA_URL"),
        access_token=_required_env("GROWHUB_HA_TOKEN"),
    )
    service = LightingApplicationService(store, client=client)
    default_dist = Path(__file__).resolve().parents[3] / "web" / "dist"
    web_dist = Path(os.environ.get("GROWHUB_WEB_DIST", default_dist))
    return create_app(service, web_dist=web_dist)
