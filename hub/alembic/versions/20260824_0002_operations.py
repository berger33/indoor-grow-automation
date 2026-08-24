"""Persiste configuração, usuários, alarmes, calibração e operação.

Revision ID: 20260824_0002
Revises: 20260824_0001
"""

from alembic import op
import sqlalchemy as sa

revision = "20260824_0002"
down_revision = "20260824_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "setpoints",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("ph", sa.Float(), nullable=False),
        sa.Column("ec_ms_cm", sa.Float(), nullable=False),
        sa.Column("air_temperature_c", sa.Float(), nullable=False),
        sa.Column("humidity_percent", sa.Float(), nullable=False),
        sa.Column("vpd_kpa", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
    op.create_table(
        "recipes",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("recipe_id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("batch_liters", sa.Float(), nullable=False),
        sa.Column("target_ph", sa.Float(), nullable=False),
        sa.Column("target_ec_ms_cm", sa.Float(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
    op.create_table(
        "recipe_steps",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("recipe_id", sa.String(64), primary_key=True),
        sa.Column("step_order", sa.Integer(), primary_key=True),
        sa.Column("channel", sa.Integer(), nullable=False),
        sa.Column("volume_ml", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["station_id", "recipe_id"], ["recipes.station_id", "recipes.recipe_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("station_id", "recipe_id", "channel", name="uq_recipe_channel"),
    )
    op.create_table(
        "irrigation_schedules",
        sa.Column("station_id", sa.String(64), primary_key=True),
        sa.Column("window_id", sa.String(64), primary_key=True),
        sa.Column("start_time", sa.String(5), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("weekdays", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(64), primary_key=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "alarms",
        sa.Column("alarm_id", sa.String(36), primary_key=True),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("cause", sa.String(500), nullable=False),
        sa.Column("procedure", sa.String(1000), nullable=False),
        sa.Column("raised_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latched", sa.Boolean(), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("acknowledged_by", sa.String(64)),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["acknowledged_by"], ["users.user_id"], ondelete="SET NULL"),
    )
    op.create_index("ix_alarms_station_raised", "alarms", ["station_id", "raised_at"])
    op.create_table(
        "command_audit",
        sa.Column("audit_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target", sa.String(128), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_command_audit_station_time", "command_audit", ["station_id", "occurred_at"])
    op.create_table(
        "calibrations",
        sa.Column("calibration_id", sa.String(36), primary_key=True),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("coefficients", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("calibrated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("calibrated_by", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["calibrated_by"], ["users.user_id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("station_id", "device_id", "calibrated_at", name="uq_calibration_device_time"),
    )
    op.create_table(
        "batch_runs",
        sa.Column("batch_id", sa.String(36), primary_key=True),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("recipe_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("current_step", sa.String(64), nullable=False),
        sa.Column("progress_percent", sa.Float(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("failure_code", sa.String(64)),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["station_id", "recipe_id"], ["recipes.station_id", "recipes.recipe_id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "realtime_outbox",
        sa.Column("event_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True, autoincrement=True),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("station_id", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.station_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_realtime_outbox_station_event", "realtime_outbox", ["station_id", "event_id"])


def downgrade() -> None:
    op.drop_index("ix_realtime_outbox_station_event", table_name="realtime_outbox")
    op.drop_table("realtime_outbox")
    op.drop_table("batch_runs")
    op.drop_table("calibrations")
    op.drop_index("ix_command_audit_station_time", table_name="command_audit")
    op.drop_table("command_audit")
    op.drop_index("ix_alarms_station_raised", table_name="alarms")
    op.drop_table("alarms")
    op.drop_table("users")
    op.drop_table("irrigation_schedules")
    op.drop_table("recipe_steps")
    op.drop_table("recipes")
    op.drop_table("setpoints")
