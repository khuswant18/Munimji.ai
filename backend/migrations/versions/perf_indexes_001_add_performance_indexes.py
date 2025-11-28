"""add_performance_indexes

Revision ID: perf_indexes_001
Revises: 8660615f8547
Create Date: 2025-11-27

Add indexes for improved query performance on frequently accessed columns.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'perf_indexes_001'
down_revision: Union[str, None] = '8660615f8547'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes."""
    # Index for ledger queries by user and date (most common query pattern)
    op.create_index(
        'ix_ledger_entries_user_created',
        'ledger_entries',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # Index for ledger queries by type
    op.create_index(
        'ix_ledger_entries_user_type',
        'ledger_entries',
        ['user_id', 'type'],
        unique=False
    )
    
    # Index for customer lookups by name
    op.create_index(
        'ix_customers_user_name',
        'customers',
        ['user_id', 'name'],
        unique=False
    )
    
    # Index for supplier lookups by name
    op.create_index(
        'ix_suppliers_user_name',
        'suppliers',
        ['user_id', 'name'],
        unique=False
    )
    
    # Index for conversations by user
    op.create_index(
        'ix_conversations_user_updated',
        'conversations',
        ['user_id', 'updated_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_ledger_entries_user_created', table_name='ledger_entries')
    op.drop_index('ix_ledger_entries_user_type', table_name='ledger_entries')
    op.drop_index('ix_customers_user_name', table_name='customers')
    op.drop_index('ix_suppliers_user_name', table_name='suppliers')
    op.drop_index('ix_conversations_user_updated', table_name='conversations')
