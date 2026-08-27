"""Add auth_accounts, refresh_sessions, roles, user_roles, and update users table.

Revision ID: c5d8e9f1a2b3
Revises: f3c7b9d2a8e1
Create Date: 2026-08-27
"""

from typing import Sequence, Union
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c5d8e9f1a2b3"
down_revision: Union[str, None] = "f3c7b9d2a8e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    now = datetime.now(timezone.utc)

    # 1. Create 'roles' table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    # 2. Create 'user_roles' table
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_index(op.f("ix_user_roles_role_id"), "user_roles", ["role_id"], unique=False)
    op.create_index(op.f("ix_user_roles_user_id"), "user_roles", ["user_id"], unique=False)

    # 3. Create 'auth_accounts' table
    op.create_table(
        "auth_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_accounts_user_id"), "auth_accounts", ["user_id"], unique=False)
    op.create_index("idx_auth_accounts_provider_acc", "auth_accounts", ["provider", "provider_account_id"], unique=True)
    op.create_index("idx_auth_accounts_user_provider", "auth_accounts", ["user_id", "provider"], unique=False)

    # 4. Create 'refresh_sessions' table
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_hash", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refresh_sessions_user_id"), "refresh_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_refresh_sessions_token_hash"), "refresh_sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_refresh_sessions_expires_at"), "refresh_sessions", ["expires_at"], unique=False)
    op.create_index(op.f("ix_refresh_sessions_revoked"), "refresh_sessions", ["revoked"], unique=False)
    op.create_index("idx_refresh_sessions_lookup", "refresh_sessions", ["token_hash", "revoked", "expires_at"], unique=False)
    op.create_index("idx_refresh_sessions_user_active", "refresh_sessions", ["user_id", "revoked"], unique=False)

    # 5. Alter 'users' table (using batch_alter_table for SQLite & Postgres compatibility)
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column("hashed_password", existing_type=sa.String(length=255), nullable=True)

    # Sync email_verified with is_verified for existing users
    op.execute("UPDATE users SET email_verified = is_verified WHERE is_verified IS NOT NULL")

    # 6. Seed base roles
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        roles_table,
        [
            {"name": "student", "description": "Ученик / Студент платформы UNTverse", "created_at": now},
            {"name": "teacher", "description": "Преподаватель / Репетитор по информатике", "created_at": now},
            {"name": "admin", "description": "Администратор системы", "created_at": now},
            {"name": "moderator", "description": "Модератор контента и заданий", "created_at": now},
        ],
    )

    # 7. Seed auth_accounts for existing users
    bind = op.get_bind()
    users_data = bind.execute(sa.text("SELECT id, email FROM users")).fetchall()
    if users_data:
        auth_accounts_table = sa.table(
            "auth_accounts",
            sa.column("user_id", sa.Integer),
            sa.column("provider", sa.String),
            sa.column("provider_account_id", sa.String),
            sa.column("provider_email", sa.String),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
        )
        accounts = [
            {
                "user_id": row[0],
                "provider": "password",
                "provider_account_id": str(row[1]).lower(),
                "provider_email": str(row[1]).lower(),
                "created_at": now,
                "updated_at": now,
            }
            for row in users_data
        ]
        op.bulk_insert(auth_accounts_table, accounts)

    # 8. Seed user_roles for existing users
    roles_rows = bind.execute(sa.text("SELECT id, name FROM roles")).fetchall()
    role_map = {row[1]: row[0] for row in roles_rows}

    users_roles_data = bind.execute(sa.text("SELECT id, role FROM users")).fetchall()
    if users_roles_data:
        user_roles_table = sa.table(
            "user_roles",
            sa.column("user_id", sa.Integer),
            sa.column("role_id", sa.Integer),
            sa.column("assigned_at", sa.DateTime(timezone=True)),
        )
        user_roles_to_insert = []
        for u_id, u_role in users_roles_data:
            r_id = role_map.get(u_role) or role_map.get("student")
            if r_id:
                user_roles_to_insert.append({
                    "user_id": u_id,
                    "role_id": r_id,
                    "assigned_at": now,
                })
        if user_roles_to_insert:
            op.bulk_insert(user_roles_table, user_roles_to_insert)


def downgrade() -> None:
    # 1. Drop user_roles
    op.drop_index(op.f("ix_user_roles_user_id"), table_name="user_roles")
    op.drop_index(op.f("ix_user_roles_role_id"), table_name="user_roles")
    op.drop_table("user_roles")

    # 2. Drop roles
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")

    # 3. Drop refresh_sessions
    op.drop_index("idx_refresh_sessions_user_active", table_name="refresh_sessions")
    op.drop_index("idx_refresh_sessions_lookup", table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_revoked"), table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_expires_at"), table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_token_hash"), table_name="refresh_sessions")
    op.drop_index(op.f("ix_refresh_sessions_user_id"), table_name="refresh_sessions")
    op.drop_table("refresh_sessions")

    # 4. Drop auth_accounts
    op.drop_index("idx_auth_accounts_user_provider", table_name="auth_accounts")
    op.drop_index("idx_auth_accounts_provider_acc", table_name="auth_accounts")
    op.drop_index(op.f("ix_auth_accounts_user_id"), table_name="auth_accounts")
    op.drop_table("auth_accounts")

    # 5. Revert users table changes
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("email_verified")
        batch_op.alter_column("hashed_password", existing_type=sa.String(length=255), nullable=False)
