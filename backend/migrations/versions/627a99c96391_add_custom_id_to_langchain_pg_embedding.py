"""add_custom_id_to_langchain_pg_embedding

Revision ID: 627a99c96391
Revises: 367038ff9564
Create Date: 2025-11-26 01:30:21.906064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '627a99c96391'
down_revision: Union[str, Sequence[str], None] = '367038ff9564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('langchain_pg_embedding', sa.Column('custom_id', sa.VARCHAR(), nullable=True))
    op.add_column('langchain_pg_embedding', sa.Column('uuid', sa.UUID(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('langchain_pg_embedding', 'uuid')
    op.drop_column('langchain_pg_embedding', 'custom_id')
