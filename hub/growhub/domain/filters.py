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
