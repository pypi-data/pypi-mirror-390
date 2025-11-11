"""rename_toolset_ids_to_skill_ids_in_teams

Revision ID: 2e4cb136dc10
Revises: d4eaf16e3f8d
Create Date: 2025-11-06 21:31:20.981166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e4cb136dc10'
down_revision: Union[str, Sequence[str], None] = 'd4eaf16e3f8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename toolset_ids to skill_ids in teams table."""
    # Rename toolset_ids column to skill_ids
    op.alter_column('teams', 'toolset_ids', new_column_name='skill_ids')


def downgrade() -> None:
    """Rename skill_ids back to toolset_ids in teams table."""
    # Reverse the column rename
    op.alter_column('teams', 'skill_ids', new_column_name='toolset_ids')
