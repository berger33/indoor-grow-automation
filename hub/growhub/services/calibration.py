"""Valida medições do assistente sem inventar confirmação física."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from ..control.pump_calibration import CalibrationPoint, PumpCalibration
from ..drivers.hx711 import LoadCellCalibration


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    kind: str
    coefficients: dict[str, object]
    status: Literal["calculated", "requires_device_ack"]
    explanation: str


def evaluate_calibration(kind: str, measurements: dict[str, object], *, device_id: str, now: datetime) -> CalibrationResult:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("calibração exige horário com timezone")
    try:
        if kind == "mass":
            tare = int(measurements["tareCounts"])
            reference = int(measurements["referenceCounts"])
            mass_kg = float(measurements["referenceMassKg"])
            if not math.isfinite(mass_kg) or not 0.1 <= mass_kg <= 50:
                raise ValueError("massa de referência fora da faixa")
            calibration = LoadCellCalibration(tare, (reference - tare) / (mass_kg * 1_000))
            return CalibrationResult(kind, calibration.to_dict(), "calculated", "Coeficiente calculado; valide removendo e recolocando a massa.")
        if kind == "pump":
            durations = measurements["durationsSeconds"]
            volumes = measurements["volumesMl"]
            if not isinstance(durations, list) or not isinstance(volumes, list) or len(durations) != 3 or len(volumes) != 3:
                raise ValueError("informe exatamente três durações e três volumes")
            fitted = PumpCalibration.fit(
                device_id,
                tuple(CalibrationPoint(float(duration), float(volume)) for duration, volume in zip(durations, volumes, strict=True)),
                supply_voltage_v=float(measurements["supplyVoltageV"]),
                calibrated_at=now,
            )
            return CalibrationResult(kind, {"flowMlS": fitted.flow_ml_s, "supplyVoltageV": fitted.supply_voltage_v, "maximumRelativeError": fitted.maximum_relative_error}, "calculated", "Curva calculada; faça uma dose de verificação antes de liberar a bomba.")
        if kind == "ph":
            standards = [float(value) for value in measurements["standardsPh"]]  # type: ignore[index]
            if len(standards) != 3 or any(abs(value - expected) > 0.2 for value, expected in zip(standards, (4.0, 7.0, 10.0), strict=True)):
                raise ValueError("use padrões pH 4,00, 7,00 e 10,00 dentro da tolerância")
            return CalibrationResult(kind, {"standardsPh": standards}, "requires_device_ack", "Padrões validados; só conclua após o ESP32 gravar e confirmar cada ponto.")
        if kind == "ec":
            standard = float(measurements["standardMsCm"])
            observed = float(measurements["observedMsCm"])
            if not math.isfinite(standard) or not math.isfinite(observed) or not 0.1 <= standard <= 20 or abs(observed - standard) / standard > 0.30:
                raise ValueError("padrão EC ou leitura inicial fora da faixa de 30%")
            return CalibrationResult(kind, {"standardMsCm": standard, "observedMsCm": observed}, "requires_device_ack", "Referência validada; só conclua após o ESP32 gravar a calibração e reler o padrão.")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        if isinstance(exc, ValueError) and str(exc):
            raise
        raise ValueError("medições de calibração incompletas ou inválidas") from exc
    raise ValueError("tipo de calibração não suportado")
