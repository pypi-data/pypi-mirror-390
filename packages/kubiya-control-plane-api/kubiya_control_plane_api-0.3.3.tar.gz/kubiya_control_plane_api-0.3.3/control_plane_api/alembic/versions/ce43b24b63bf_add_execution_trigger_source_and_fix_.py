"""add_execution_trigger_source_and_fix_types

Revision ID: ce43b24b63bf
Revises: 89e127caa47d
Create Date: 2025-11-06 20:15:09.289858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce43b24b63bf'
down_revision: Union[str, Sequence[str], None] = '89e127caa47d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add trigger_source enum type
    op.execute("""
        CREATE TYPE executiontriggersource AS ENUM (
            'user', 'job_cron', 'job_webhook', 'job_manual', 'system', 'api', 'chat'
        )
    """)

    # 2. Add trigger_source and trigger_metadata columns to executions table
    op.add_column('executions',
        sa.Column('trigger_source', sa.Enum(
            'user', 'job_cron', 'job_webhook', 'job_manual', 'system', 'api', 'chat',
            name='executiontriggersource'
        ), nullable=False, server_default='user')
    )
    op.add_column('executions',
        sa.Column('trigger_metadata', sa.JSON(), server_default='{}', nullable=True)
    )

    # 3. Create index on trigger_source
    op.create_index('ix_executions_trigger_source', 'executions', ['trigger_source'])

    # 4. Fix jobs table column types (total_executions, successful_executions, failed_executions from JSON to INTEGER)
    # First, convert any existing data
    op.execute("UPDATE jobs SET total_executions = COALESCE((total_executions::text)::integer, 0) WHERE total_executions IS NOT NULL")
    op.execute("UPDATE jobs SET successful_executions = COALESCE((successful_executions::text)::integer, 0) WHERE successful_executions IS NOT NULL")
    op.execute("UPDATE jobs SET failed_executions = COALESCE((failed_executions::text)::integer, 0) WHERE failed_executions IS NOT NULL")

    # Then alter column types
    op.alter_column('jobs', 'total_executions',
        type_=sa.Integer(),
        existing_type=sa.JSON(),
        server_default='0',
        nullable=False
    )
    op.alter_column('jobs', 'successful_executions',
        type_=sa.Integer(),
        existing_type=sa.JSON(),
        server_default='0',
        nullable=False
    )
    op.alter_column('jobs', 'failed_executions',
        type_=sa.Integer(),
        existing_type=sa.JSON(),
        server_default='0',
        nullable=False
    )

    # 5. Fix job_executions.execution_duration_ms from JSON to INTEGER
    op.execute("UPDATE job_executions SET execution_duration_ms = COALESCE((execution_duration_ms::text)::integer, NULL) WHERE execution_duration_ms IS NOT NULL")
    op.alter_column('job_executions', 'execution_duration_ms',
        type_=sa.Integer(),
        existing_type=sa.JSON(),
        nullable=True
    )

    # 6. Update last_execution_id in jobs to be UUID type instead of VARCHAR
    # First drop the existing column (safe since we're still setting up)
    op.drop_column('jobs', 'last_execution_id')

    # Add it back with correct UUID type
    op.add_column('jobs',
        sa.Column('last_execution_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 7. Update execution_id in job_executions to be UUID type
    op.drop_column('job_executions', 'execution_id')
    op.add_column('job_executions',
        sa.Column('execution_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)
    )
    op.create_index('idx_job_executions_execution_id', 'job_executions', ['execution_id'])

    # 8. Now add the foreign key constraints with proper types
    op.create_foreign_key(
        'fk_jobs_last_execution',
        'jobs', 'executions',
        ['last_execution_id'], ['id'],
        ondelete='SET NULL'
    )

    op.create_foreign_key(
        'fk_job_executions_execution',
        'job_executions', 'executions',
        ['execution_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign keys
    op.drop_constraint('fk_job_executions_execution', 'job_executions', type_='foreignkey')
    op.drop_constraint('fk_jobs_last_execution', 'jobs', type_='foreignkey')

    # Revert execution_id in job_executions back to VARCHAR
    op.drop_index('idx_job_executions_execution_id', 'job_executions')
    op.drop_column('job_executions', 'execution_id')
    op.add_column('job_executions',
        sa.Column('execution_id', sa.String(255), nullable=False)
    )

    # Revert last_execution_id in jobs back to VARCHAR
    op.drop_column('jobs', 'last_execution_id')
    op.add_column('jobs',
        sa.Column('last_execution_id', sa.String(255), nullable=True)
    )

    # Revert execution_duration_ms back to JSON
    op.alter_column('job_executions', 'execution_duration_ms',
        type_=sa.JSON(),
        existing_type=sa.Integer()
    )

    # Revert job execution counters back to JSON
    op.alter_column('jobs', 'failed_executions',
        type_=sa.JSON(),
        existing_type=sa.Integer()
    )
    op.alter_column('jobs', 'successful_executions',
        type_=sa.JSON(),
        existing_type=sa.Integer()
    )
    op.alter_column('jobs', 'total_executions',
        type_=sa.JSON(),
        existing_type=sa.Integer()
    )

    # Drop trigger_source index and columns
    op.drop_index('ix_executions_trigger_source', 'executions')
    op.drop_column('executions', 'trigger_metadata')
    op.drop_column('executions', 'trigger_source')

    # Drop enum type
    op.execute("DROP TYPE executiontriggersource")
