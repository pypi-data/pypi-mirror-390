from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from control_plane_api.app.database import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow(Base):
    """Workflow model for storing workflow information"""

    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(WorkflowStatus, values_callable=lambda x: [e.value for e in x]), default=WorkflowStatus.PENDING, nullable=False)

    # Workflow definition
    steps = Column(JSON, default=list, nullable=False)
    current_step = Column(String, nullable=True)

    # Configuration
    configuration = Column(JSON, default=dict, nullable=False)

    # Relationships
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # State management
    state = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="workflows")

    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name}, status={self.status})>"
