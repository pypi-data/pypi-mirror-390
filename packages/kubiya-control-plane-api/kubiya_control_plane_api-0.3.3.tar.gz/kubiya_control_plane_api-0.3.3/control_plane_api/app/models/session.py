from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from control_plane_api.app.database import Base


class Session(Base):
    """Session model for storing agent session information with multi-user support"""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)

    # Multi-user support - inspired by Agno's multi-user pattern
    user_id = Column(String, nullable=True, index=True)  # User who owns this session
    user_email = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_avatar = Column(String, nullable=True)

    # Session data
    messages = Column(JSON, default=list, nullable=False)
    context = Column(JSON, default=dict, nullable=False)
    session_metadata = Column(JSON, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, agent_id={self.agent_id}, user_id={self.user_id})>"
