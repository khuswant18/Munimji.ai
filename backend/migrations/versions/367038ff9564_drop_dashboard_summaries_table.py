"""drop dashboard_summaries table

Revision ID: 367038ff9564
Revises: f63e14cc8ba2
Create Date: 2025-11-26 00:59:48.669833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '367038ff9564'
down_revision: Union[str, Sequence[str], None] = 'f63e14cc8ba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TABLE dashboard_summaries CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    pass
