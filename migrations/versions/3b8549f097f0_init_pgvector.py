"""init pgvector

Revision ID: 3b8549f097f0
Revises: 
Create Date: 2025-11-25 11:40:29.503132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b8549f097f0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    pass


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
    pass
