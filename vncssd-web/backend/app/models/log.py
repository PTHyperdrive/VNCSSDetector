"""
VNCSSDetector Web Service - Log Models
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Any

from sqlalchemy import String, Enum, DateTime, Text, BigInteger, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LogLevel(str, PyEnum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SystemLog(Base):
    """System log entries from nodes."""
    
    __tablename__ = "system_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    node_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        index=True
    )
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel), 
        nullable=False, 
        index=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        index=True
    )
    
    # Relationships
    node = relationship("Node", back_populates="system_logs")
    
    def __repr__(self) -> str:
        return f"<SystemLog {self.level}: {self.source}>"


class AuditLog(Base):
    """Audit log for tracking user actions."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        index=True
    )
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.resource_type}>"
