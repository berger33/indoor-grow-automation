"""Adaptadores para serviços externos ao núcleo de cultivo."""

from .home_assistant import HomeAssistantSwitchClient, SwitchObservation

__all__ = ["HomeAssistantSwitchClient", "SwitchObservation"]
