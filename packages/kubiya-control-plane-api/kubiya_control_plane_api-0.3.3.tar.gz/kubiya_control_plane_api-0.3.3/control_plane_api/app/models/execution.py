from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from control_plane_api.app.database import Base


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionType(str, enum.Enum):
    AGENT = "agent"
    TEAM = "team"
    WORKFLOW = "workflow"


class ExecutionTriggerSource(str, enum.Enum):
    """How the execution was triggered"""
    USER = "user"  # Triggered by a user directly via UI/API
    JOB_CRON = "job_cron"  # Triggered by a scheduled job (cron)
    JOB_WEBHOOK = "job_webhook"  # Triggered by a webhook job
    JOB_MANUAL = "job_manual"  # Triggered manually through job trigger API
    SYSTEM = "system"  # Triggered by system/automation
    API = "api"  # Triggered directly via API
    CHAT = "chat"  # Triggered from chat interface


class Execution(Base):
    """Model for tracking agent/team/workflow executions with user attribution"""

    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization
    organization_id = Column(String, nullable=False, index=True)

    # What is being executed
    execution_type = Column(SQLEnum(ExecutionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    entity_id = Column(String, nullable=False)  # agent_id, team_id, or workflow_id
    entity_name = Column(String)  # Cached name for display
    runner_name = Column(String, nullable=True)  # Cached runner name for filtering

    # User attribution - who initiated this execution
    user_id = Column(String, nullable=True, index=True)
    user_email = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_avatar = Column(String, nullable=True)

    # Trigger source - how this execution was initiated
    trigger_source = Column(
        SQLEnum(ExecutionTriggerSource, values_callable=lambda x: [e.value for e in x]),
        default=ExecutionTriggerSource.USER,
        nullable=False,
        index=True
    )
    trigger_metadata = Column(JSON, default={})  # Additional context about the trigger (job_id, webhook payload, etc.)

    # Execution details
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    config = Column(JSON, default={})

    # Status and results
    status = Column(SQLEnum(ExecutionStatus, values_callable=lambda x: [e.value for e in x]), default=ExecutionStatus.PENDING, nullable=False)
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    usage = Column(JSON, default={})  # Token usage, cost, etc.
    execution_metadata = Column(JSON, default={})  # Additional metadata

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    participants = relationship("ExecutionParticipant", back_populates="execution", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Execution {self.id} ({self.execution_type}:{self.entity_id}) - {self.status} by {self.user_email}>"
