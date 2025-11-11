"""add_runtime_column_to_teams_simple

Revision ID: b0e10697f212
Revises: 1382bec74309
Create Date: 2025-11-06 11:48:06.515460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0e10697f212'
down_revision: Union[str, Sequence[str], None] = '1382bec74309'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add runtime column to teams table."""
    # Create the RuntimeType enum if it doesn't exist
    op.execute("CREATE TYPE runtimetype AS ENUM ('default', 'claude_code')")

    # Add runtime column to teams table
    op.add_column('teams', sa.Column('runtime', sa.Enum('default', 'claude_code', name='runtimetype'), server_default='default', nullable=False))

    # Create index on runtime column
    op.create_index(op.f('ix_teams_runtime'), 'teams', ['runtime'], unique=False)


def downgrade() -> None:
    """Downgrade schema: Remove runtime column from teams table."""
    # Drop index
    op.drop_index(op.f('ix_teams_runtime'), table_name='teams')

    # Drop column
    op.drop_column('teams', 'runtime')

    # Drop enum type
    op.execute("DROP TYPE runtimetype")
