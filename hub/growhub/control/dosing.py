"""Intertravamentos e limites independentes para dosagem química."""

from __future__ import annotations

from enum import StrEnum


class PHChannel(StrEnum):
    UP = "ph_up"
    DOWN = "ph_down"


class PHDirectionInterlock:
    def __init__(self) -> None:
        self._active: PHChannel | None = None
        self._blocked = False

    @property
    def active(self) -> PHChannel | None:
        return self._active

    def request(self, channel: PHChannel) -> None:
        if self._blocked:
            raise PermissionError("intertravamento de pH está bloqueado")
        if self._active is not None and self._active is not channel:
            self._active = None
            self._blocked = True
            raise RuntimeError("pH up e pH down jamais podem operar juntos")
        self._active = channel

    def stop(self, channel: PHChannel) -> None:
        if self._active is channel:
            self._active = None

    def reset(self) -> None:
        if self._active is not None:
            raise PermissionError("desligue os canais de pH antes do rearme")
        self._blocked = False
