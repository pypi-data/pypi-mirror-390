"""rename metadata to custom_metadata

Revision ID: efa2dc427da1
Revises: 1f54bc2a37e3
Create Date: 2025-01-08 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efa2dc427da1'
down_revision = '1f54bc2a37e3'
branch_labels = None
depends_on = None


def upgrade():
    # Rename metadata to custom_metadata in execution_tool_calls
    op.alter_column('execution_tool_calls', 'metadata', new_column_name='custom_metadata')

    # Rename metadata to custom_metadata in execution_tasks
    op.alter_column('execution_tasks', 'metadata', new_column_name='custom_metadata')


def downgrade():
    # Revert custom_metadata back to metadata in execution_tasks
    op.alter_column('execution_tasks', 'custom_metadata', new_column_name='metadata')

    # Revert custom_metadata back to metadata in execution_tool_calls
    op.alter_column('execution_tool_calls', 'custom_metadata', new_column_name='metadata')
