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
