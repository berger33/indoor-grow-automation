"""Cria estações, sensores, telemetria e persistência EKAZA.

Revision ID: 20260824_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20260824_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stations",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "sensors",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("sensor_id", sa.String(64), primary_key=True),
        sa.Column("node_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("unit", sa.String(24), nullable=False),
        sa.Column("maximum_age_seconds", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
    op.create_table(
        "telemetry",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True, autoincrement=True),
        sa.Column("message_id", sa.String(36), nullable=False, unique=True),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("sensor_id", sa.String(64), nullable=False),
        sa.Column("sequence", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(24), nullable=False),
        sa.Column("quality", sa.String(24), nullable=False),
        sa.Column("error_code", sa.String(64)),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id", "sensor_id"], ["sensors.station_id", "sensors.sensor_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("station_id", "sensor_id", "sequence", name="uq_telemetry_sensor_sequence"),
    )
    op.create_index("ix_telemetry_observed_at", "telemetry", ["observed_at"])
    op.create_table(
        "telemetry_hourly",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("sensor_id", sa.String(64), primary_key=True),
        sa.Column("bucket_at", sa.DateTime(timezone=True), primary_key=True),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("unit", sa.String(24), nullable=False),
        sa.Column("minimum", sa.Float(), nullable=False),
        sa.Column("maximum", sa.Float(), nullable=False),
        sa.Column("average", sa.Float(), nullable=False),
        sa.Column("samples", sa.Integer(), nullable=False),
        sa.Column("quality_counts", sa.JSON(), nullable=False),
    )
    op.create_table(
        "lighting_schedules",
        sa.Column("entity_id", sa.String(160), primary_key=True),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("on_time", sa.String(5), nullable=False),
        sa.Column("off_time", sa.String(5), nullable=False),
        sa.Column("weekdays", sa.JSON(), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "lighting_overrides",
        sa.Column("entity_id", sa.String(160), primary_key=True),
        sa.Column("state", sa.String(3), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["lighting_schedules.entity_id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("lighting_overrides")
    op.drop_table("lighting_schedules")
    op.drop_table("telemetry_hourly")
    op.drop_index("ix_telemetry_observed_at", table_name="telemetry")
    op.drop_table("telemetry")
    op.drop_table("sensors")
    op.drop_table("stations")
