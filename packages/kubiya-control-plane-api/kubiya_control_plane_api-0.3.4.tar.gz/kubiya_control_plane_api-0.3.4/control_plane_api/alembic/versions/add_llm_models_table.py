"""add llm_models table

Revision ID: add_llm_models_table
Revises: f973b431d1ce
Create Date: 2025-01-08 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_llm_models_table'
down_revision = 'f973b431d1ce'
branch_labels = None
depends_on = None


def upgrade():
    # Create llm_models table
    op.create_table(
        'llm_models',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('logo', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('recommended', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('compatible_runtimes', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('pricing', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_llm_models_value'), 'llm_models', ['value'], unique=True)
    op.create_index(op.f('ix_llm_models_provider'), 'llm_models', ['provider'], unique=False)
    op.create_index(op.f('ix_llm_models_enabled'), 'llm_models', ['enabled'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_llm_models_enabled'), table_name='llm_models')
    op.drop_index(op.f('ix_llm_models_provider'), table_name='llm_models')
    op.drop_index(op.f('ix_llm_models_value'), table_name='llm_models')
    op.drop_table('llm_models')
