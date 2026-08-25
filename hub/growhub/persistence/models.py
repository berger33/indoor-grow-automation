"""Modelo relacional inicial compatível com PostgreSQL e SQLite de teste."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class StationRow(Base):
    __tablename__ = "stations"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(64), default="America/Sao_Paulo")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SensorRow(Base):
    __tablename__ = "sensors"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    node_id: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(40))
    unit: Mapped[str] = mapped_column(String(24))
    maximum_age_seconds: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )


class TelemetryRow(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    station_id: Mapped[str] = mapped_column(String(64), nullable=False)
    sensor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(24), nullable=False)
    quality: Mapped[str] = mapped_column(String(24), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(64))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["station_id", "sensor_id"],
            ["sensors.station_id", "sensors.sensor_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("station_id", "sensor_id", "sequence", name="uq_telemetry_sensor_sequence"),
    )


class TelemetryHourlyRow(Base):
    __tablename__ = "telemetry_hourly"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    bucket_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    kind: Mapped[str] = mapped_column(String(40))
    unit: Mapped[str] = mapped_column(String(24))
    minimum: Mapped[float] = mapped_column(Float)
    maximum: Mapped[float] = mapped_column(Float)
    average: Mapped[float] = mapped_column(Float)
    samples: Mapped[int] = mapped_column(Integer)
    quality_counts: Mapped[dict[str, int]] = mapped_column(JSON)


class LightingScheduleRow(Base):
    __tablename__ = "lighting_schedules"

    entity_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    label: Mapped[str] = mapped_column(String(120))
    on_time: Mapped[str] = mapped_column(String(5))
    off_time: Mapped[str] = mapped_column(String(5))
    weekdays: Mapped[list[int]] = mapped_column(JSON)
    timezone: Mapped[str] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LightingOverrideRow(Base):
    __tablename__ = "lighting_overrides"

    entity_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    state: Mapped[str] = mapped_column(String(3))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        ForeignKeyConstraint(
            ["entity_id"], ["lighting_schedules.entity_id"], ondelete="CASCADE"
        ),
    )


class SetpointsRow(Base):
    __tablename__ = "setpoints"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ph: Mapped[float] = mapped_column(Float)
    ec_ms_cm: Mapped[float] = mapped_column(Float)
    air_temperature_c: Mapped[float] = mapped_column(Float)
    humidity_percent: Mapped[float] = mapped_column(Float)
    vpd_kpa: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[str] = mapped_column(String(64))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )


class RecipeRow(Base):
    __tablename__ = "recipes"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    recipe_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    batch_liters: Mapped[float] = mapped_column(Float)
    target_ph: Mapped[float] = mapped_column(Float)
    target_ec_ms_cm: Mapped[float] = mapped_column(Float)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )


class RecipeStepRow(Base):
    __tablename__ = "recipe_steps"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    recipe_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    step_order: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel: Mapped[int] = mapped_column(Integer)
    volume_ml: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        ForeignKeyConstraint(
            ["station_id", "recipe_id"],
            ["recipes.station_id", "recipes.recipe_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("station_id", "recipe_id", "channel", name="uq_recipe_channel"),
    )


class IrrigationScheduleRow(Base):
    __tablename__ = "irrigation_schedules"

    station_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    start_time: Mapped[str] = mapped_column(String(5))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    weekdays: Mapped[list[int]] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )


class UserRow(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(16))
    password_hash: Mapped[str] = mapped_column(String(256))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AlarmRow(Base):
    __tablename__ = "alarms"

    alarm_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    station_id: Mapped[str] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    cause: Mapped[str] = mapped_column(String(500))
    procedure: Mapped[str] = mapped_column(String(1000))
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latched: Mapped[bool] = mapped_column(Boolean, default=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[str | None] = mapped_column(String(64))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["acknowledged_by"], ["users.user_id"], ondelete="SET NULL"),
    )


class CommandAuditRow(Base):
    __tablename__ = "command_audit"

    audit_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    station_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(24))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    details: Mapped[dict[str, object]] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="RESTRICT"),
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="RESTRICT"),
    )


class CalibrationRow(Base):
    __tablename__ = "calibrations"

    calibration_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    station_id: Mapped[str] = mapped_column(String(64))
    device_id: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(32))
    coefficients: Mapped[dict[str, object]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(24))
    calibrated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    calibrated_by: Mapped[str] = mapped_column(String(64))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["calibrated_by"], ["users.user_id"], ondelete="RESTRICT"),
        UniqueConstraint("station_id", "device_id", "calibrated_at", name="uq_calibration_device_time"),
    )


class BatchRunRow(Base):
    __tablename__ = "batch_runs"

    batch_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    station_id: Mapped[str] = mapped_column(String(64))
    recipe_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(24))
    current_step: Mapped[str] = mapped_column(String(64))
    progress_percent: Mapped[float] = mapped_column(Float)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_code: Mapped[str | None] = mapped_column(String(64))

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="RESTRICT"),
        ForeignKeyConstraint(
            ["station_id", "recipe_id"],
            ["recipes.station_id", "recipes.recipe_id"],
            ondelete="RESTRICT",
        ),
    )


class RealtimeOutboxRow(Base):
    __tablename__ = "realtime_outbox"

    event_id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64))
    station_id: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
