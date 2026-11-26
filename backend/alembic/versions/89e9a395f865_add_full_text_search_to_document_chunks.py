"""add full text search to document chunks

Revision ID: 89e9a395f865
Revises: 0dc4c93bdd38
Create Date: 2026-11-23 17:49:25.382748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e9a395f865'
down_revision: Union[str, Sequence[str], None] = '0dc4c93bdd38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE document_chunks
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english', content)
        ) STORED
        """
    )

    op.execute(
        """
        CREATE INDEX ix_document_chunks_search_vector
        ON document_chunks
        USING GIN (search_vector)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_document_chunks_search_vector
        """
    )

    op.execute(
        """
        ALTER TABLE document_chunks
        DROP COLUMN IF EXISTS search_vector
        """
    )
