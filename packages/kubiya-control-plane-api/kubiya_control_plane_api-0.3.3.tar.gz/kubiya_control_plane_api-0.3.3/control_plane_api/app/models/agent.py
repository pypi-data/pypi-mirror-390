from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from control_plane_api.app.database import Base


class AgentStatus(str, enum.Enum):
    """Agent status enumeration"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class RuntimeType(str, enum.Enum):
    """Agent runtime type enumeration"""

    DEFAULT = "default"  # Agno-based runtime (current implementation)
    CLAUDE_CODE = "claude_code"  # Claude Code SDK runtime


class Agent(Base):
    """Agent model for storing agent information"""

    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(AgentStatus, values_callable=lambda x: [e.value for e in x]), default=AgentStatus.IDLE, nullable=False)
    capabilities = Column(JSON, default=list, nullable=False)
    configuration = Column(JSON, default=dict, nullable=False)

    # LiteLLM configuration
    model_id = Column(String, nullable=True)  # LiteLLM model identifier
    model_config = Column(JSON, default=dict, nullable=False)  # Model-specific config (temperature, top_p, etc.)

    # Runtime configuration
    runtime = Column(
        Enum(RuntimeType, values_callable=lambda x: [e.value for e in x]),
        default=RuntimeType.DEFAULT,
        server_default="default",
        nullable=False,
        index=True
    )  # Runtime type for agent execution (default: Agno, claude_code: Claude Code SDK)

    # Foreign keys
    organization_id = Column(String, nullable=False, index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, nullable=True)

    # State management
    state = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="agents")
    sessions = relationship("Session", back_populates="agent", cascade="all, delete-orphan")

    # Many-to-many relationship with environments
    environment_associations = relationship(
        "AgentEnvironment",
        foreign_keys="AgentEnvironment.agent_id",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, status={self.status})>"
