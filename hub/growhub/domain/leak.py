"""Detecção local de vazamento com retenção até rearme seguro."""

from __future__ import annotations


class LeakLatch:
    def __init__(self, *, wet_confirmations: int = 3, dry_confirmations: int = 5) -> None:
        for name, value in (
            ("wet_confirmations", wet_confirmations),
            ("dry_confirmations", dry_confirmations),
        ):
            if isinstance(value, bool) or not 1 <= value <= 100:
                raise ValueError(f"{name} deve estar entre 1 e 100")
        self._wet_required = wet_confirmations
        self._dry_required = dry_confirmations
        self._wet_count = 0
        self._dry_count = 0
        self._latched = False

    @property
    def latched(self) -> bool:
        return self._latched

    @property
    def reset_permitted(self) -> bool:
        return self._latched and self._dry_count >= self._dry_required

    def update(self, wet: bool) -> bool:
        if not isinstance(wet, bool):
            raise TypeError("estado de vazamento deve ser bool")
        if wet:
            self._wet_count += 1
            self._dry_count = 0
            if self._wet_count >= self._wet_required:
                self._latched = True
        else:
            self._wet_count = 0
            if self._latched:
                self._dry_count += 1
        return self._latched

    def reset(self) -> bool:
        """Rearma somente após confirmação seca; nunca rearma automaticamente."""
        if not self.reset_permitted:
            return False
        self._latched = False
        self._wet_count = 0
        self._dry_count = 0
        return True
