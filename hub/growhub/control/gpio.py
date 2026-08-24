"""Modelo de inicialização segura para saídas GPIO/registradores."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OutputDefinition:
    output_id: str
    active_high: bool

    @property
    def safe_electrical_level(self) -> bool:
        return not self.active_high


class SafeOutputBank:
    def __init__(self, definitions: tuple[OutputDefinition, ...]) -> None:
        if not definitions:
            raise ValueError("banco de saídas não pode ser vazio")
        ids = [item.output_id for item in definitions]
        if len(ids) != len(set(ids)):
            raise ValueError("output_id duplicado")
        self._definitions = {item.output_id: item for item in definitions}
        self._logical = {output_id: False for output_id in ids}
        self._initialized = False
        self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    def initialize_safe_levels(self) -> dict[str, bool]:
        self._logical = {output_id: False for output_id in self._definitions}
        self._enabled = False
        self._initialized = True
        return self.electrical_levels()

    def enable(self) -> None:
        if not self._initialized:
            raise PermissionError("níveis seguros precisam ser inicializados primeiro")
        self._enabled = True

    def command(self, output_id: str, on: bool) -> None:
        if output_id not in self._definitions:
            raise KeyError(output_id)
        if not isinstance(on, bool):
            raise TypeError("comando de saída deve ser bool")
        if on and not self._enabled:
            raise PermissionError("banco de saídas está inibido")
        self._logical[output_id] = on

    def emergency_disable(self) -> dict[str, bool]:
        self._enabled = False
        self._logical = {output_id: False for output_id in self._definitions}
        return self.electrical_levels()

    def electrical_levels(self) -> dict[str, bool]:
        return {
            output_id: definition.active_high
            if self._logical[output_id]
            else definition.safe_electrical_level
            for output_id, definition in self._definitions.items()
        }
