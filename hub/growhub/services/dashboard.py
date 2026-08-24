"""View models do painel que separam comando, observação e feedback."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..domain.remote_lighting import LightState
from .remote_lighting import ReconciliationResult


class ControlTileStatus(StrEnum):
    CONFIRMED = "confirmed"
    DIVERGENT = "divergent"
    INHIBITED = "inhibited"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ControlTile:
    control_id: str
    desired_on: bool
    observed_on: bool | None
    feedback_confirmed: bool
    status: ControlTileStatus
    explanation: str


def remote_light_tile(result: ReconciliationResult) -> ControlTile:
    confirmed = result.confirmed and result.desired is result.observed
    return ControlTile(
        control_id=result.entity_id,
        desired_on=result.desired is LightState.ON,
        observed_on=result.observed is LightState.ON,
        feedback_confirmed=confirmed,
        status=(
            ControlTileStatus.CONFIRMED if confirmed else ControlTileStatus.DIVERGENT
        ),
        explanation=(
            f"estado confirmado via Home Assistant ({result.source})"
            if confirmed
            else "comando enviado, mas a tomada não confirmou o estado"
        ),
    )


def local_actuator_tile(
    control_id: str,
    *,
    desired_on: bool,
    observed_on: bool | None,
    feedback_confirmed: bool,
    inhibit_reason: str | None = None,
) -> ControlTile:
    if inhibit_reason:
        return ControlTile(
            control_id,
            False,
            observed_on,
            False,
            ControlTileStatus.INHIBITED,
            inhibit_reason,
        )
    if observed_on is None:
        return ControlTile(
            control_id,
            desired_on,
            None,
            False,
            ControlTileStatus.UNAVAILABLE,
            "estado observado indisponível",
        )
    confirmed = feedback_confirmed and desired_on is observed_on
    return ControlTile(
        control_id,
        desired_on,
        observed_on,
        confirmed,
        ControlTileStatus.CONFIRMED if confirmed else ControlTileStatus.DIVERGENT,
        "feedback físico confirmado"
        if confirmed
        else "comando, estado e feedback físico não coincidem",
    )
