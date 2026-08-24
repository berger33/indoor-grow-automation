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
