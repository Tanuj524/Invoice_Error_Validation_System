"""make source_format not nullable

Revision ID: 8707e8acf12e
Revises: 1ae55e490da4
Create Date: 2026-07-22 12:38:11.510229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8707e8acf12e'
down_revision: Union[str, Sequence[str], None] = '1ae55e490da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'invoices', 'source_format',
        existing_type=sa.Enum('PDF', 'EXCEL', 'IMAGE', name='sourceformat'),
        nullable=False,
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'invoices', 'source_format',
        existing_type=sa.Enum('PDF', 'EXCEL', 'IMAGE', name='sourceformat'),
        nullable=True,
    )
  
