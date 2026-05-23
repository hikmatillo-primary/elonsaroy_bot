"""Initial schema: users and ads tables

Revision ID: 001
Revises:
Create Date: 2026-05-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    category_enum = postgresql.ENUM(
        "auto", "realestate", "phone", "jobs", name="category_enum", create_type=False
    )
    category_enum.create(op.get_bind(), checkfirst=True)

    status_enum = postgresql.ENUM(
        "draft", "pending", "approved", "rejected",
        name="ad_status_enum", create_type=False,
    )
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "ads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category", category_enum, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.String(100), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=False),
        sa.Column("photo_file_ids", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("status", status_enum, nullable=False, server_default="draft"),
        sa.Column("admin_message_id", sa.BigInteger(), nullable=True),
        sa.Column("main_channel_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ads")
    op.execute("DROP TYPE IF EXISTS ad_status_enum")
    op.execute("DROP TYPE IF EXISTS category_enum")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
