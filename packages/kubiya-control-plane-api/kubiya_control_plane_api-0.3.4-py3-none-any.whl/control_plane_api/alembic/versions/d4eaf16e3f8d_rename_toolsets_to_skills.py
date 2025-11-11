"""rename_skills_to_skills

Revision ID: d4eaf16e3f8d
Revises: ce43b24b63bf
Create Date: 2025-11-06 20:58:29.015408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4eaf16e3f8d'
down_revision: Union[str, Sequence[str], None] = 'ce43b24b63bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Rename toolsets to skills."""

    # Rename enum type from toolset_type to skill_type
    op.execute("ALTER TYPE toolset_type RENAME TO skill_type")

    # Rename toolsets table to skills
    op.rename_table('toolsets', 'skills')

    # Rename toolset_associations table to skill_associations
    op.rename_table('toolset_associations', 'skill_associations')

    # Rename columns in skills table
    op.alter_column('skills', 'type', new_column_name='skill_type')

    # Rename column in skill_associations table
    op.alter_column('skill_associations', 'toolset_id', new_column_name='skill_id')

    # Update index names
    op.execute("ALTER INDEX IF EXISTS idx_toolsets_org RENAME TO idx_skills_org")
    op.execute("ALTER INDEX IF EXISTS idx_toolsets_type RENAME TO idx_skills_type")
    op.execute("ALTER INDEX IF EXISTS idx_toolsets_enabled RENAME TO idx_skills_enabled")

    op.execute("ALTER INDEX IF EXISTS idx_toolset_associations_org RENAME TO idx_skill_associations_org")
    op.execute("ALTER INDEX IF EXISTS idx_toolset_associations_toolset RENAME TO idx_skill_associations_skill")
    op.execute("ALTER INDEX IF EXISTS idx_toolset_associations_entity RENAME TO idx_skill_associations_entity")

    # Update constraint names (actual constraint is named unique_toolset_association)
    op.execute("ALTER TABLE skill_associations RENAME CONSTRAINT unique_toolset_association TO unique_skill_entity")

    # Update table comments
    op.execute("COMMENT ON TABLE skills IS 'Skill definitions with type-specific configurations'")
    op.execute("COMMENT ON TABLE skill_associations IS 'Associates skills with agents, teams, or environments'")


def downgrade() -> None:
    """Downgrade schema: Rename skills back to toolsets."""

    # Reverse table comments
    op.execute("COMMENT ON TABLE skill_associations IS 'Associates toolsets with agents, teams, or environments'")
    op.execute("COMMENT ON TABLE skills IS 'Toolset definitions with type-specific configurations'")

    # Reverse constraint names
    op.execute("ALTER TABLE skill_associations RENAME CONSTRAINT unique_skill_entity TO unique_toolset_association")

    # Reverse index names
    op.execute("ALTER INDEX IF EXISTS idx_skill_associations_entity RENAME TO idx_toolset_associations_entity")
    op.execute("ALTER INDEX IF EXISTS idx_skill_associations_skill RENAME TO idx_toolset_associations_toolset")
    op.execute("ALTER INDEX IF EXISTS idx_skill_associations_org RENAME TO idx_toolset_associations_org")

    op.execute("ALTER INDEX IF EXISTS idx_skills_enabled RENAME TO idx_toolsets_enabled")
    op.execute("ALTER INDEX IF EXISTS idx_skills_type RENAME TO idx_toolsets_type")
    op.execute("ALTER INDEX IF EXISTS idx_skills_org RENAME TO idx_toolsets_org")

    # Reverse column renames
    op.alter_column('skill_associations', 'skill_id', new_column_name='toolset_id')
    op.alter_column('skills', 'skill_type', new_column_name='type')

    # Reverse table renames
    op.rename_table('skill_associations', 'toolset_associations')
    op.rename_table('skills', 'toolsets')

    # Reverse enum type rename
    op.execute("ALTER TYPE skill_type RENAME TO toolset_type")
