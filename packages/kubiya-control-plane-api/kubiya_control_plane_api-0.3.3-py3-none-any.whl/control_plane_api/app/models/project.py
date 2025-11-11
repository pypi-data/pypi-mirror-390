from sqlalchemy import Column, String, DateTime, Text, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from control_plane_api.app.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    PAUSED = "paused"


class Project(Base):
    """Project model for organizing agents, teams, and tasks"""

    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus, values_callable=lambda x: [e.value for e in x]), default=ProjectStatus.ACTIVE, nullable=False)

    # Environment and runner configuration
    restrict_to_environment = Column(Boolean, default=False, nullable=False)
    # Note: policy_ids are stored in settings JSON field, not as separate column

    # Default settings for project
    default_model = Column(String, nullable=True)  # Default LLM model for this project
    default_settings = Column(JSON, default=dict, nullable=False)  # Additional project-wide settings

    # Metadata
    is_default = Column(Boolean, default=False, nullable=False)  # Flag for the default project
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Note: Project associations are managed through junction tables (project_agents, project_teams)
    # in Supabase, not through direct foreign keys in the SQLAlchemy models

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
