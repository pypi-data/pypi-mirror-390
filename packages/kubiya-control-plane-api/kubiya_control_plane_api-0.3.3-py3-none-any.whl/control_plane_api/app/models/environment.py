"""Environment model for execution environments"""
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum
from datetime import datetime
import uuid
import enum

from control_plane_api.app.database import Base


class EnvironmentStatus(str, enum.Enum):
    """Environment status"""
    PENDING = "pending"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class Environment(Base):
    """
    Execution environment - represents a worker queue environment.
    Maps to task queues in Temporal.
    """

    __tablename__ = "environments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, nullable=False, index=True)
    
    # Basic info
    name = Column(String, nullable=False, index=True)  # Environment name (e.g., "default", "production")
    display_name = Column(String, nullable=True)  # User-friendly display name
    description = Column(String, nullable=True)
    
    # Configuration
    tags = Column(JSON, nullable=False, default=list)  # Tags for categorization
    settings = Column(JSON, nullable=False, default=dict)  # Environment-specific settings
    status = Column(
        SQLEnum(EnvironmentStatus),
        nullable=False,
        default=EnvironmentStatus.PENDING,
        index=True
    )
    
    # Temporal Cloud provisioning
    worker_token = Column(String, nullable=True)  # JWT token for worker registration
    provisioning_workflow_id = Column(String, nullable=True)  # Temporal workflow ID for provisioning
    provisioned_at = Column(DateTime, nullable=True)  # When namespace was provisioned
    error_message = Column(String, nullable=True)  # Error message if provisioning failed
    temporal_namespace_id = Column(String, nullable=True)  # Temporal Cloud namespace ID
    
    # Execution environment configuration (env vars, secrets, integrations)
    execution_environment = Column(JSON, nullable=False, default=dict)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)  # User email or ID who created
    updated_by = Column(String, nullable=True)  # User email or ID who last updated

    def __repr__(self):
        return f"<Environment(id={self.id}, name={self.name}, organization_id={self.organization_id}, status={self.status})>"

