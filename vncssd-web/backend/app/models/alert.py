"""
VNCSSDetector Web Service - Alert Model
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Boolean, Enum, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlertSeverity(str, PyEnum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    """Alert model for notifications and warnings."""
    
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    recording_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recordings.id", ondelete="SET NULL")
    )
    analysis_result_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("analysis_results.id", ondelete="SET NULL")
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity), 
        nullable=False, 
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_acknowledged: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        index=True
    )
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        index=True
    )
    
    # Relationships
    node = relationship("Node", back_populates="alerts")
    recording = relationship("Recording", back_populates="alerts")
    analysis_result = relationship("AnalysisResult", back_populates="alerts")
    acknowledged_by_user = relationship("User", back_populates="acknowledged_alerts")
    
    def __repr__(self) -> str:
        return f"<Alert {self.severity}: {self.title}>"
