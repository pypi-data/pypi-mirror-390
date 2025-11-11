"""add_skill_templates_table

Revision ID: 31cd69a644ce
Revises: f973b431d1ce
Create Date: 2025-11-08 10:35:32.991694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31cd69a644ce'
down_revision: Union[str, Sequence[str], None] = 'f973b431d1ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
