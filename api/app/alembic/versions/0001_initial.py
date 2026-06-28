"""initial schema

Creates all tables: users, employees, role_permissions, conversations,
messages, documents, projects, project_members, settings, refresh_tokens,
activity_logs. Includes indexes for hot read paths.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CITEXT for case-insensitive email comparison
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, index=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "theme", sa.String(), nullable=False, server_default=sa.text("'dark'")
        ),
        sa.Column(
            "must_reset_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("employee_id", sa.String(), nullable=False, unique=True),
        sa.Column("phone_number", sa.String(), nullable=False, server_default=""),
        sa.Column("designation", sa.String(), nullable=False, server_default=""),
        sa.Column("department", sa.String(), nullable=False, server_default="", index=True),
        sa.Column(
            "manager_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("office_location", sa.String(), nullable=False, server_default=""),
        sa.Column("leave_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("salary", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column(
            "projects",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "permissions",
        sa.Column("name", sa.String(), primary_key=True),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role", sa.String(), primary_key=True),
        sa.Column(
            "permission",
            sa.String(),
            sa.ForeignKey("permissions.name", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False, server_default="New conversation"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_conversations_user_updated",
        "conversations",
        ["user_id", sa.text("updated_at DESC")],
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("feedback", sa.String(), nullable=True),
        sa.Column("tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('user','assistant','system')", name="messages_role_check"),
        sa.CheckConstraint(
            "feedback IS NULL OR feedback IN ('up','down')", name="messages_feedback_check"
        ),
    )
    op.create_index("ix_messages_conversation", "messages", ["conversation_id", "created_at"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("doc_type", sa.String(), nullable=False, server_default="policy"),
        sa.Column("department", sa.String(), nullable=False, server_default="HR"),
        sa.Column(
            "required_role",
            sa.String(),
            nullable=False,
            server_default="all",
            index=True,
        ),
        sa.Column("source_path", sa.String(), nullable=True),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "uploaded_by",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "doc_type IN ('policy','handbook','memo','form')",
            name="documents_doc_type_check",
        ),
        sa.CheckConstraint(
            "required_role IN ('all','employee','manager','hr','admin')",
            name="documents_required_role_check",
        ),
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status", sa.String(), nullable=False, server_default="active", index=True
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('active','paused','completed','archived')",
            name="projects_status_check",
        ),
    )

    op.create_table(
        "project_members",
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="contributor",
        ),
        sa.Column(
            "added_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "settings",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("theme", sa.String(), nullable=False, server_default="dark"),
        sa.Column("language", sa.String(), nullable=False, server_default="en"),
        sa.Column(
            "notification_prefs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "anonymized_telemetry",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "token_hash",
            sa.String(),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "replaced_by",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("ip", postgresql.INET(), nullable=True),
    )

    op.create_table(
        "activity_logs",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=False),
            primary_key=True,
        ),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(), nullable=False, index=True),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("ip", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )


def downgrade() -> None:
    for table in (
        "activity_logs",
        "refresh_tokens",
        "settings",
        "project_members",
        "projects",
        "documents",
        "messages",
        "conversations",
        "role_permissions",
        "permissions",
        "employees",
        "users",
    ):
        op.drop_table(table)