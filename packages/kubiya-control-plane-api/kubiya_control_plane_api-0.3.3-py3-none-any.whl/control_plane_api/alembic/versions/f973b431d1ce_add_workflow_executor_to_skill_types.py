"""add_workflow_executor_to_skill_types

Revision ID: f973b431d1ce
Revises: 2e4cb136dc10
Create Date: 2025-11-07 14:27:34.063089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f973b431d1ce'
down_revision: Union[str, Sequence[str], None] = '2e4cb136dc10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing constraint
    op.execute("ALTER TABLE skills DROP CONSTRAINT IF EXISTS toolsets_type_check")

    # Add constraint with workflow_executor included
    op.execute("""
        ALTER TABLE skills ADD CONSTRAINT toolsets_type_check
        CHECK (skill_type IN ('file_system', 'shell', 'python', 'docker', 'sleep',
                       'file_generation', 'data_visualization', 'workflow_executor', 'custom'))
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop existing constraint
    op.execute("ALTER TABLE skills DROP CONSTRAINT IF EXISTS toolsets_type_check")

    # Add constraint without workflow_executor
    op.execute("""
        ALTER TABLE skills ADD CONSTRAINT toolsets_type_check
        CHECK (skill_type IN ('file_system', 'shell', 'python', 'docker', 'sleep',
                       'file_generation', 'data_visualization', 'custom'))
    """)
