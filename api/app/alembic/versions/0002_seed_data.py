"""Seed RBAC matrix (mirrors core/rbac.py). Idempotent."""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_seed_data"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_PERMISSIONS = {
    "employee": [
        "read_public_docs",
        "read_engineering_docs",
    ],
    "manager": [
        "read_public_docs",
        "read_engineering_docs",
        "read_hr_policies",
    ],
    "hr": [
        "read_public_docs",
        "read_engineering_docs",
        "read_hr_policies",
        "read_finance_docs",
        "view_all_profiles",
    ],
    "admin": [
        "read_public_docs",
        "read_hr_policies",
        "read_finance_docs",
        "read_engineering_docs",
        "read_restricted_docs",
        "view_all_profiles",
        "manage_users",
        "upload_docs",
        "view_audit_log",
    ],
}

ALL_PERMISSIONS = sorted({p for perms in ROLE_PERMISSIONS.values() for p in perms})


def upgrade() -> None:
    bind = op.get_bind()
    # permissions
    for perm in ALL_PERMISSIONS:
        bind.execute(
            sa.text(
                "INSERT INTO permissions(name) VALUES (:p) ON CONFLICT (name) DO NOTHING"
            ),
            {"p": perm},
        )
    # role_permissions
    for role, perms in ROLE_PERMISSIONS.items():
        for perm in perms:
            bind.execute(
                sa.text(
                    "INSERT INTO role_permissions(role, permission) "
                    "VALUES (:r, :p) ON CONFLICT DO NOTHING"
                ),
                {"r": role, "p": perm},
            )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM role_permissions"))
    bind.execute(sa.text("DELETE FROM permissions"))