"""Association tables for many-to-many relationships"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from control_plane_api.app.database import Base


class ParticipantRole(str, enum.Enum):
    """Role of a participant in an execution"""
    OWNER = "owner"  # User who created the execution
    COLLABORATOR = "collaborator"  # User actively participating
    VIEWER = "viewer"  # User with read-only access


class AgentEnvironment(Base):
    """Many-to-many association between agents and environments"""

    __tablename__ = "agent_environments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    environment_id = Column(String, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String, nullable=False, index=True)

    # Assignment metadata
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<AgentEnvironment(agent_id={self.agent_id}, environment_id={self.environment_id})>"


class TeamEnvironment(Base):
    """Many-to-many association between teams and environments"""

    __tablename__ = "team_environments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    environment_id = Column(String, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String, nullable=False, index=True)

    # Assignment metadata
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<TeamEnvironment(team_id={self.team_id}, environment_id={self.environment_id})>"


class ExecutionParticipant(Base):
    """Many-to-many association between executions and users (multiplayer support)"""

    __tablename__ = "execution_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)

    # User information
    user_id = Column(String, nullable=False, index=True)
    user_email = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_avatar = Column(String, nullable=True)

    # Participant role and status
    role = Column(SQLEnum(ParticipantRole, values_callable=lambda x: [e.value for e in x]), default=ParticipantRole.COLLABORATOR, nullable=False)

    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    execution = relationship("Execution", back_populates="participants")

    def __repr__(self):
        return f"<ExecutionParticipant(execution_id={self.execution_id}, user_id={self.user_id}, role={self.role})>"
