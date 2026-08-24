"""Composição de produção do hub a partir de configuração de ambiente."""

from __future__ import annotations

import os
from datetime import UTC, datetime, time
from pathlib import Path

from .app import create_app
from ..domain.remote_lighting import RemoteLightSchedule
from ..integrations.home_assistant import HomeAssistantSwitchClient
from ..persistence.database import create_database_engine, create_session_factory
from ..persistence.lighting import SqlLightingStore
from ..persistence.operations import SqlOperations
from ..persistence.security import SqlUserRepository
from ..domain.sensors import EXPECTED_UNIT, SensorKind
from ..domain.staleness import DEFAULT_MAX_AGE
from ..services.lighting_application import LightingApplicationService
from ..services.operations import SensorDefinition, Setpoints, StationDefinition
from ..services.realtime import RealtimeBuffer
from ..services.security import AuthService, UserRole


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
    auth = AuthService(
        _required_env("GROWHUB_SESSION_KEY").encode(),
        repository=SqlUserRepository(sessions),
    )
    admin_id = os.environ.get("GROWHUB_ADMIN_USER", "admin").strip()
    if not auth.has_users:
        auth.add_user(
            admin_id,
            os.environ.get("GROWHUB_ADMIN_NAME", "Administrador local").strip(),
            UserRole.ADMIN,
            _required_env("GROWHUB_ADMIN_PASSWORD"),
        )
    operations = SqlOperations(sessions)
    station_id = os.environ.get("GROWHUB_STATION_ID", "grow-01").strip()
    station = StationDefinition(
        station_id,
        os.environ.get("GROWHUB_STATION_NAME", "Estufa principal").strip(),
    )
    sensor_layout = (
        ("ph_tank", "pH do tanque", SensorKind.PH, "fertigation"),
        ("ec_tank", "EC do tanque", SensorKind.EC, "fertigation"),
        ("water_temperature", "Temperatura da água", SensorKind.WATER_TEMPERATURE, "fertigation"),
        ("air_temperature", "Temperatura do ar", SensorKind.AIR_TEMPERATURE, "climate"),
        ("leaf_temperature", "Temperatura foliar", SensorKind.LEAF_TEMPERATURE, "climate"),
        ("humidity", "Umidade relativa", SensorKind.HUMIDITY, "climate"),
        ("co2", "CO₂", SensorKind.CO2, "climate"),
        ("reservoir_level", "Nível do reservatório", SensorKind.RESERVOIR_LEVEL, "fertigation"),
        ("reservoir_mass", "Massa do reservatório", SensorKind.MASS, "fertigation"),
        ("vpd", "VPD", SensorKind.VPD, "climate"),
        ("flow", "Vazão", SensorKind.FLOW, "fertigation"),
        ("leak", "Detector de vazamento", SensorKind.LEAK, "safety"),
    )
    operations.bootstrap_station(
        station,
        tuple(
            (
                SensorDefinition(station_id, sensor_id, label, int(DEFAULT_MAX_AGE[kind].total_seconds())),
                node,
                kind.value,
                EXPECTED_UNIT[kind].value,
            )
            for sensor_id, label, kind, node in sensor_layout
        ),
        now=datetime.now(UTC),
    )
    if station_id not in operations.setpoints:
        operations.save_setpoints(station_id, Setpoints(5.8, 1.8, 25, 65, 1.1), user_id=admin_id, now=datetime.now(UTC))
    default_dist = Path(__file__).resolve().parents[3] / "web" / "dist"
    web_dist = Path(os.environ.get("GROWHUB_WEB_DIST", default_dist))
    return create_app(
        service,
        web_dist=web_dist,
        operations=operations,
        auth=auth,
        realtime=RealtimeBuffer(),
    )
