"""add comprehensive analytics tables for execution tracking

Revision ID: 1f54bc2a37e3
Revises: add_llm_models_table
Create Date: 2025-01-08 14:00:00.000000

This migration adds production-grade analytics tables to track:
- Per-turn LLM metrics (tokens, duration, cost)
- Tool execution details (success/failure, timing)
- Task completion tracking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1f54bc2a37e3'
down_revision = 'add_llm_models_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create execution_turns table
    op.create_table(
        'execution_turns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('turn_id', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_read_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('cache_creation_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('input_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('output_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('cache_read_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('cache_creation_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('finish_reason', sa.String(), nullable=True),
        sa.Column('response_preview', sa.Text(), nullable=True),
        sa.Column('tools_called_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tools_called_names', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('runtime_minutes', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('model_weight', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('tool_calls_weight', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('aem_value', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('aem_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE')
    )

    # Create indexes for execution_turns
    op.create_index('ix_execution_turns_organization_id', 'execution_turns', ['organization_id'])
    op.create_index('ix_execution_turns_execution_id', 'execution_turns', ['execution_id'])
    op.create_index('ix_execution_turns_org_execution', 'execution_turns', ['organization_id', 'execution_id'])
    op.create_index('ix_execution_turns_org_model', 'execution_turns', ['organization_id', 'model'])
    op.create_index('ix_execution_turns_org_created', 'execution_turns', ['organization_id', 'created_at'])
    op.create_index('ix_execution_turns_org_cost', 'execution_turns', ['organization_id', 'total_cost'])

    # Create execution_tool_calls table
    op.create_table(
        'execution_tool_calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('turn_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tool_name', sa.String(), nullable=False),
        sa.Column('tool_use_id', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('tool_input', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_output', sa.Text(), nullable=True),
        sa.Column('tool_output_size', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_type', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['turn_id'], ['execution_turns.id'], ondelete='CASCADE')
    )

    # Create indexes for execution_tool_calls
    op.create_index('ix_execution_tool_calls_organization_id', 'execution_tool_calls', ['organization_id'])
    op.create_index('ix_execution_tool_calls_execution_id', 'execution_tool_calls', ['execution_id'])
    op.create_index('ix_execution_tool_calls_turn_id', 'execution_tool_calls', ['turn_id'])
    op.create_index('ix_execution_tool_calls_tool_name', 'execution_tool_calls', ['tool_name'])
    op.create_index('ix_execution_tool_calls_org_execution', 'execution_tool_calls', ['organization_id', 'execution_id'])
    op.create_index('ix_execution_tool_calls_org_tool', 'execution_tool_calls', ['organization_id', 'tool_name'])
    op.create_index('ix_execution_tool_calls_org_success', 'execution_tool_calls', ['organization_id', 'success'])
    op.create_index('ix_execution_tool_calls_org_created', 'execution_tool_calls', ['organization_id', 'created_at'])

    # Create execution_tasks table
    op.create_table(
        'execution_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_number', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('task_type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE')
    )

    # Create indexes for execution_tasks
    op.create_index('ix_execution_tasks_organization_id', 'execution_tasks', ['organization_id'])
    op.create_index('ix_execution_tasks_execution_id', 'execution_tasks', ['execution_id'])
    op.create_index('ix_execution_tasks_org_execution', 'execution_tasks', ['organization_id', 'execution_id'])
    op.create_index('ix_execution_tasks_org_status', 'execution_tasks', ['organization_id', 'status'])


def downgrade():
    # Drop execution_tasks table and indexes
    op.drop_index('ix_execution_tasks_org_status', table_name='execution_tasks')
    op.drop_index('ix_execution_tasks_org_execution', table_name='execution_tasks')
    op.drop_index('ix_execution_tasks_execution_id', table_name='execution_tasks')
    op.drop_index('ix_execution_tasks_organization_id', table_name='execution_tasks')
    op.drop_table('execution_tasks')

    # Drop execution_tool_calls table and indexes
    op.drop_index('ix_execution_tool_calls_org_created', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_org_success', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_org_tool', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_org_execution', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_tool_name', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_turn_id', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_execution_id', table_name='execution_tool_calls')
    op.drop_index('ix_execution_tool_calls_organization_id', table_name='execution_tool_calls')
    op.drop_table('execution_tool_calls')

    # Drop execution_turns table and indexes
    op.drop_index('ix_execution_turns_org_cost', table_name='execution_turns')
    op.drop_index('ix_execution_turns_org_created', table_name='execution_turns')
    op.drop_index('ix_execution_turns_org_model', table_name='execution_turns')
    op.drop_index('ix_execution_turns_org_execution', table_name='execution_turns')
    op.drop_index('ix_execution_turns_execution_id', table_name='execution_turns')
    op.drop_index('ix_execution_turns_organization_id', table_name='execution_turns')
    op.drop_table('execution_turns')
