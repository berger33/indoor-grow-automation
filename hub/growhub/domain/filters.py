"""Filtros determinísticos para aquisição de sensores."""

from __future__ import annotations

import math
from collections import deque
from statistics import median


class MedianFilter:
    """Janela deslizante de mediana sem preencher amostras inexistentes."""

    def __init__(self, window_size: int) -> None:
        if isinstance(window_size, bool) or not 1 <= window_size <= 101:
            raise ValueError("window_size deve estar entre 1 e 101")
        self._samples: deque[float] = deque(maxlen=window_size)

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    def add(self, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("amostra deve ser finita")
        self._samples.append(float(value))
        return float(median(self._samples))


class MovingAverageFilter:
    """Média móvel com acumulador incremental e janela limitada."""

    def __init__(self, window_size: int) -> None:
        if isinstance(window_size, bool) or not 1 <= window_size <= 10_000:
            raise ValueError("window_size deve estar entre 1 e 10000")
        self._samples: deque[float] = deque()
        self._window_size = window_size
        self._sum = 0.0

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    def add(self, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("amostra deve ser finita")
        sample = float(value)
        self._samples.append(sample)
        self._sum += sample
        if len(self._samples) > self._window_size:
            self._sum -= self._samples.popleft()
        return self._sum / len(self._samples)


class BooleanDebouncer:
    """Confirma uma transição somente após N amostras digitais iguais."""

    def __init__(self, required_consecutive: int, *, initial: bool | None = None) -> None:
        if (
            isinstance(required_consecutive, bool)
            or not 1 <= required_consecutive <= 100
        ):
            raise ValueError("required_consecutive deve estar entre 1 e 100")
        self._required = required_consecutive
        self._stable = initial
        self._candidate: bool | None = None
        self._count = 0

    @property
    def stable(self) -> bool | None:
        return self._stable

    def update(self, raw: bool) -> bool | None:
        if not isinstance(raw, bool):
            raise TypeError("entrada digital deve ser bool")
        if raw == self._stable:
            self._candidate = None
            self._count = 0
            return self._stable
        if raw != self._candidate:
            self._candidate = raw
            self._count = 1
        else:
            self._count += 1
        if self._count >= self._required:
            self._stable = raw
            self._candidate = None
            self._count = 0
        return self._stable
