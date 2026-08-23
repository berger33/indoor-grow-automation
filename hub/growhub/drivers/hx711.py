"""Calibração persistível de plataforma de pesagem HX711."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class LoadCellCalibration:
    tare_counts: int
    counts_per_gram: float

    def __post_init__(self) -> None:
        if isinstance(self.tare_counts, bool) or not isinstance(self.tare_counts, int):
            raise TypeError("tare_counts deve ser inteiro")
        if not math.isfinite(self.counts_per_gram) or self.counts_per_gram <= 0:
            raise ValueError("counts_per_gram deve ser positivo e finito")

    def mass_kg(self, raw_counts: int) -> float:
        if isinstance(raw_counts, bool) or not isinstance(raw_counts, int):
            raise TypeError("raw_counts deve ser inteiro")
        return (raw_counts - self.tare_counts) / self.counts_per_gram / 1_000.0

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> LoadCellCalibration:
        if set(data) != {"tare_counts", "counts_per_gram"}:
            raise ValueError("campos de calibração HX711 inválidos")
        return cls(
            tare_counts=data["tare_counts"],
            counts_per_gram=data["counts_per_gram"],
        )
