"""add_jobs_and_job_executions_tables

Revision ID: 89e127caa47d
Revises: b0e10697f212
Create Date: 2025-11-06 20:11:04.561446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e127caa47d'
down_revision: Union[str, Sequence[str], None] = 'b0e10697f212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('organization_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('cron_schedule', sa.String(255), nullable=True),
        sa.Column('cron_timezone', sa.String(100), server_default='UTC'),
        sa.Column('webhook_url_path', sa.String(500), nullable=True),
        sa.Column('webhook_secret', sa.String(500), nullable=True),
        sa.Column('temporal_schedule_id', sa.String(255), nullable=True),
        sa.Column('planning_mode', sa.String(50), nullable=False, server_default='predefined_agent'),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(255), nullable=True),
        sa.Column('entity_name', sa.String(255), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('executor_type', sa.String(50), nullable=False, server_default='auto'),
        sa.Column('worker_queue_name', sa.String(255), nullable=True),
        sa.Column('environment_name', sa.String(255), nullable=True),
        sa.Column('config', sa.JSON(), server_default='{}'),
        sa.Column('execution_environment', sa.JSON(), server_default='{}'),
        sa.Column('last_execution_id', sa.String(255), nullable=True),
        sa.Column('last_execution_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_execution_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_executions', sa.Integer(), server_default='0'),
        sa.Column('successful_executions', sa.Integer(), server_default='0'),
        sa.Column('failed_executions', sa.Integer(), server_default='0'),
        sa.Column('execution_history', sa.JSON(), server_default='[]'),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Note: Skipping foreign key constraint for last_execution_id due to type mismatch
    # The executions.id is stored as UUID in the database but defined as String in models
    # We can add this constraint later after resolving the type discrepancy

    # Add unique constraints
    op.create_unique_constraint('uq_jobs_webhook_url_path', 'jobs', ['webhook_url_path'])
    op.create_unique_constraint('uq_jobs_temporal_schedule_id', 'jobs', ['temporal_schedule_id'])

    # Create indexes for jobs table
    op.create_index('idx_jobs_organization_id', 'jobs', ['organization_id'])
    op.create_index('idx_jobs_name', 'jobs', ['organization_id', 'name'])
    op.create_index('idx_jobs_enabled', 'jobs', ['enabled'])
    op.create_index('idx_jobs_status', 'jobs', ['status'])
    op.create_index('idx_jobs_trigger_type', 'jobs', ['trigger_type'])
    op.create_index('idx_jobs_webhook_url_path', 'jobs', ['webhook_url_path'])
    op.create_index('idx_jobs_temporal_schedule_id', 'jobs', ['temporal_schedule_id'])
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('idx_jobs_next_execution_at', 'jobs', ['next_execution_at'])

    # Create job_executions table
    op.create_table(
        'job_executions',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('job_id', sa.String(255), nullable=False),
        sa.Column('execution_id', sa.String(255), nullable=False),
        sa.Column('organization_id', sa.String(255), nullable=False),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('trigger_metadata', sa.JSON(), server_default='{}'),
        sa.Column('execution_status', sa.String(50), nullable=True),
        sa.Column('execution_duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Add foreign key constraints for job_executions
    op.create_foreign_key(
        'fk_job_executions_job',
        'job_executions', 'jobs',
        ['job_id'], ['id'],
        ondelete='CASCADE'
    )
    # Note: Skipping foreign key for execution_id due to type mismatch with executions.id

    # Create indexes for job_executions table
    op.create_index('idx_job_executions_job_id', 'job_executions', ['job_id'])
    op.create_index('idx_job_executions_execution_id', 'job_executions', ['execution_id'])
    op.create_index('idx_job_executions_organization_id', 'job_executions', ['organization_id'])
    op.create_index('idx_job_executions_created_at', 'job_executions', ['created_at'])
    op.create_index('idx_job_executions_trigger_type', 'job_executions', ['trigger_type'])
    op.create_index('idx_job_executions_execution_status', 'job_executions', ['execution_status'])

    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for jobs table
    op.execute("""
        DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
        CREATE TRIGGER update_jobs_updated_at
            BEFORE UPDATE ON jobs
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;")

    # Drop indexes for job_executions
    op.drop_index('idx_job_executions_execution_status', 'job_executions')
    op.drop_index('idx_job_executions_trigger_type', 'job_executions')
    op.drop_index('idx_job_executions_created_at', 'job_executions')
    op.drop_index('idx_job_executions_organization_id', 'job_executions')
    op.drop_index('idx_job_executions_execution_id', 'job_executions')
    op.drop_index('idx_job_executions_job_id', 'job_executions')

    # Drop indexes for jobs
    op.drop_index('idx_jobs_next_execution_at', 'jobs')
    op.drop_index('idx_jobs_created_at', 'jobs')
    op.drop_index('idx_jobs_temporal_schedule_id', 'jobs')
    op.drop_index('idx_jobs_webhook_url_path', 'jobs')
    op.drop_index('idx_jobs_trigger_type', 'jobs')
    op.drop_index('idx_jobs_status', 'jobs')
    op.drop_index('idx_jobs_enabled', 'jobs')
    op.drop_index('idx_jobs_name', 'jobs')
    op.drop_index('idx_jobs_organization_id', 'jobs')

    # Drop tables
    op.drop_table('job_executions')
    op.drop_table('jobs')
