"""Cliente mínimo da API REST do Home Assistant para tomadas remotas."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ENTITY_ID = re.compile(r"^switch\.[a-z0-9_]+$")


class JsonTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None = None,
    ) -> Any: ...


class UrllibJsonTransport:
    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None = None,
    ) -> Any:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ConnectionError("falha na API do Home Assistant") from exc


@dataclass(frozen=True, slots=True)
class SwitchObservation:
    entity_id: str
    is_on: bool
    observed_at: datetime


class HomeAssistantSwitchClient:
    def __init__(
        self,
        *,
        base_url: str,
        access_token: str,
        transport: JsonTransport | None = None,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url do Home Assistant inválida")
        if not access_token or access_token.isspace():
            raise ValueError("access_token deve vir de segredo de runtime")
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self._transport = transport or UrllibJsonTransport()

    def set_switch(self, entity_id: str, *, on: bool) -> SwitchObservation:
        self._validate_entity(entity_id)
        if not isinstance(on, bool):
            raise TypeError("on deve ser bool")
        service = "turn_on" if on else "turn_off"
        self._transport.request(
            "POST",
            f"{self._base_url}/api/services/switch/{service}",
            self._headers,
            {"entity_id": entity_id},
        )
        return self.read_switch(entity_id)

    def read_switch(self, entity_id: str) -> SwitchObservation:
        self._validate_entity(entity_id)
        response = self._transport.request(
            "GET",
            f"{self._base_url}/api/states/{entity_id}",
            self._headers,
        )
        if not isinstance(response, dict) or response.get("state") not in {"on", "off"}:
            raise ValueError("estado da tomada ausente ou não suportado")
        return SwitchObservation(
            entity_id=entity_id,
            is_on=response["state"] == "on",
            observed_at=datetime.now(UTC),
        )

    @staticmethod
    def _validate_entity(entity_id: str) -> None:
        if not ENTITY_ID.fullmatch(entity_id):
            raise ValueError("entity_id deve ser switch válido")
