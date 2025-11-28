"""change context column to JSONB

Revision ID: 9237a687f0eb
Revises: e3fc4da163d5
Create Date: 2025-11-25 21:33:22.247606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9237a687f0eb'
down_revision: Union[str, Sequence[str], None] = 'e3fc4da163d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change context column from JSON to JSONB
    op.alter_column('conversations', 'context',
                    type_=sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
                    existing_type=sa.dialects.postgresql.JSON(astext_type=sa.Text()))


def downgrade() -> None:
    """Downgrade schema."""
    # Change context column back from JSONB to JSON
    op.alter_column('conversations', 'context',
                    type_=sa.dialects.postgresql.JSON(astext_type=sa.Text()),
                    existing_type=sa.dialects.postgresql.JSONB(astext_type=sa.Text()))
