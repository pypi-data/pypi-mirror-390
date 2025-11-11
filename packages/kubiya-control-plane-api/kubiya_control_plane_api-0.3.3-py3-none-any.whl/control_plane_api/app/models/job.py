from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from control_plane_api.app.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    DISABLED = "disabled"


class JobTriggerType(str, enum.Enum):
    """Job trigger type enumeration"""
    CRON = "cron"
    WEBHOOK = "webhook"
    MANUAL = "manual"


class ExecutorType(str, enum.Enum):
    """Job executor routing type"""
    AUTO = "auto"  # First available worker queue with active workers
    SPECIFIC_QUEUE = "specific_queue"  # Explicit worker queue selection
    ENVIRONMENT = "environment"  # Route to specific environment


class PlanningMode(str, enum.Enum):
    """Planning mode for job execution"""
    ON_THE_FLY = "on_the_fly"  # Use planner to determine execution
    PREDEFINED_AGENT = "predefined_agent"  # Execute specific agent
    PREDEFINED_TEAM = "predefined_team"  # Execute specific team
    PREDEFINED_WORKFLOW = "predefined_workflow"  # Execute specific workflow


class Job(Base):
    """
    Model for scheduled and webhook-triggered jobs.

    Jobs can be triggered via:
    - Cron schedule (using Temporal Schedules)
    - Webhook URL (with HMAC signature verification)
    - Manual API trigger

    Jobs execute agents, teams, or workflows with configurable routing.
    """

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: f"job_{uuid.uuid4()}")

    # Organization (multi-tenant isolation)
    organization_id = Column(String, nullable=False, index=True)

    # Job metadata
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    status = Column(
        SQLEnum(JobStatus, values_callable=lambda x: [e.value for e in x]),
        default=JobStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # Trigger configuration
    trigger_type = Column(
        SQLEnum(JobTriggerType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )

    # Cron configuration (for CRON trigger type)
    cron_schedule = Column(String, nullable=True)  # e.g., "0 17 * * *" (daily at 5pm)
    cron_timezone = Column(String, default="UTC", nullable=True)  # e.g., "America/New_York"

    # Webhook configuration (for WEBHOOK trigger type)
    webhook_url_path = Column(String, nullable=True, unique=True, index=True)  # e.g., "/api/v1/jobs/webhook/abc123"
    webhook_secret = Column(String, nullable=True)  # HMAC secret for signature verification

    # Temporal Schedule ID (managed by system)
    temporal_schedule_id = Column(String, nullable=True, unique=True, index=True)

    # Planning and execution configuration
    planning_mode = Column(
        SQLEnum(PlanningMode, values_callable=lambda x: [e.value for e in x]),
        default=PlanningMode.PREDEFINED_AGENT,
        nullable=False
    )

    # Entity to execute (based on planning_mode)
    entity_type = Column(String, nullable=True)  # "agent", "team", "workflow" (for predefined modes)
    entity_id = Column(String, nullable=True)  # agent_id, team_id, or workflow_id
    entity_name = Column(String, nullable=True)  # Cached name for display

    # Prompt configuration
    prompt_template = Column(Text, nullable=False)  # Can include {{variables}} for dynamic params
    system_prompt = Column(Text, nullable=True)

    # Executor routing configuration
    executor_type = Column(
        SQLEnum(ExecutorType, values_callable=lambda x: [e.value for e in x]),
        default=ExecutorType.AUTO,
        nullable=False
    )
    worker_queue_name = Column(String, nullable=True)  # For SPECIFIC_QUEUE executor type
    environment_name = Column(String, nullable=True)  # For ENVIRONMENT executor type

    # Execution configuration
    config = Column(JSON, default={})  # Additional execution config (timeout, retry, etc.)
    execution_environment = Column(JSON, default={})  # Environment variables, secrets, etc.

    # Execution tracking
    last_execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True)
    last_execution_at = Column(DateTime(timezone=True), nullable=True)
    next_execution_at = Column(DateTime(timezone=True), nullable=True)  # For cron jobs
    total_executions = Column(Integer, default=0, nullable=False)  # Total number of executions
    successful_executions = Column(Integer, default=0, nullable=False)  # Number of successful executions
    failed_executions = Column(Integer, default=0, nullable=False)  # Number of failed executions

    # Execution history (last N runs)
    execution_history = Column(JSON, default=list)  # List of recent execution summaries

    # Audit fields
    created_by = Column(String, nullable=True)  # User ID who created the job
    updated_by = Column(String, nullable=True)  # User ID who last updated the job

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)  # Last time job was triggered (manual or scheduled)

    # Relationships
    last_execution = relationship("Execution", foreign_keys=[last_execution_id], lazy="select")

    def __repr__(self):
        return f"<Job {self.id} ({self.name}) - {self.trigger_type}:{self.status}>"


class JobExecution(Base):
    """
    Junction table linking Jobs to Executions.
    Tracks which executions were triggered by which jobs.
    """

    __tablename__ = "job_executions"

    id = Column(String, primary_key=True, default=lambda: f"jobexec_{uuid.uuid4()}")

    # Foreign keys
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Organization (for efficient querying)
    organization_id = Column(String, nullable=False, index=True)

    # Trigger context
    trigger_type = Column(String, nullable=False)  # "cron", "webhook", "manual"
    trigger_metadata = Column(JSON, default={})  # Additional context (webhook payload, manual trigger user, etc.)

    # Execution outcome (denormalized for quick queries)
    execution_status = Column(String, nullable=True)  # Cached from execution.status
    execution_duration_ms = Column(Integer, nullable=True)  # Duration in milliseconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", foreign_keys=[job_id], lazy="select")
    execution = relationship("Execution", foreign_keys=[execution_id], lazy="select")

    def __repr__(self):
        return f"<JobExecution job={self.job_id} execution={self.execution_id}>"
