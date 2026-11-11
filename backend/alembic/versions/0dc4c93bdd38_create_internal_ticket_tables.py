"""create internal ticket tables

Revision ID: 0dc4c93bdd38
Revises: 8185c3129135
Create Date: 2026-11-11 16:00:39.164198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dc4c93bdd38'
down_revision: Union[str, Sequence[str], None] = '8185c3129135'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "ticket_number",
            sa.String(length=30),
            nullable=False,
            unique=True,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column(
            "priority",
            sa.String(length=20),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="pending_approval",
        ),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("approved_by", sa.String(length=255), nullable=True),
        sa.Column("external_provider", sa.String(length=50), nullable=True),
        sa.Column("external_ticket_id", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_index(
        "ix_tickets_status",
        "tickets",
        ["status"],
    )

    op.create_index(
        "ix_tickets_created_at",
        "tickets",
        ["created_at"],
    )

    op.create_table(
        "ticket_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "ticket_id",
            sa.BigInteger(),
            sa.ForeignKey("tickets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("old_status", sa.String(length=30), nullable=True),
        sa.Column("new_status", sa.String(length=30), nullable=True),
        sa.Column("performed_by", sa.String(length=255), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_index(
        "ix_ticket_events_ticket_id",
        "ticket_events",
        ["ticket_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ticket_events_ticket_id",
        table_name="ticket_events",
    )

    op.drop_table("ticket_events")

    op.drop_index(
        "ix_tickets_created_at",
        table_name="tickets",
    )

    op.drop_index(
        "ix_tickets_status",
        table_name="tickets",
    )

    op.drop_table("tickets")
