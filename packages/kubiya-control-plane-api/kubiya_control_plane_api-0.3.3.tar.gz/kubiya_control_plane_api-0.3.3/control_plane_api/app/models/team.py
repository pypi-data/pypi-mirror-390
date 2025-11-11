from sqlalchemy import Column, String, DateTime, Text, JSON, Enum, ForeignKey, UniqueConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid as uuid_module

from control_plane_api.app.database import Base
from control_plane_api.app.models.agent import RuntimeType


class TeamStatus(str, enum.Enum):
    """Team status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Team(Base):
    """Team model for storing team information"""

    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_team_org_name'),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid_module.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(TeamStatus, values_callable=lambda x: [e.value for e in x]), default=TeamStatus.ACTIVE, nullable=False)

    # Configuration
    configuration = Column(JSON, default=dict, nullable=False)
    # Use PostgreSQL UUID array - SQLAlchemy will handle the conversion
    skill_ids = Column(ARRAY(PG_UUID(as_uuid=False)), default=list, nullable=False)
    execution_environment = Column(JSON, default=dict, nullable=False)

    # Runtime configuration
    runtime = Column(
        Enum(RuntimeType, values_callable=lambda x: [e.value for e in x]),
        default=RuntimeType.DEFAULT,
        server_default="default",
        nullable=False,
        index=True
    )  # Runtime type for team execution (default: Agno, claude_code: Claude Code SDK)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    agents = relationship("Agent", back_populates="team")
    workflows = relationship("Workflow", back_populates="team", cascade="all, delete-orphan")

    # Many-to-many relationship with environments
    environment_associations = relationship(
        "TeamEnvironment",
        foreign_keys="TeamEnvironment.team_id",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, status={self.status})>"
