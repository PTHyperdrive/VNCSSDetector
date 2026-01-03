"""
VNCSSDetector Web Service - Analysis Result Model
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Any

from sqlalchemy import String, Enum, DateTime, Text, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventType(str, PyEnum):
    """Analysis event type/severity."""
    INFORMATIONAL = "informational"
    WARNING = "warning"
    CRITICAL = "critical"


class AnalysisResult(Base):
    """Analysis result from QMDL file analysis."""
    
    __tablename__ = "analysis_results"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recording_id: Mapped[int] = mapped_column(
        ForeignKey("recordings.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType), 
        nullable=False, 
        index=True
    )
    analyzer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    
    # Relationships
    recording = relationship("Recording", back_populates="analysis_results")
    alerts = relationship("Alert", back_populates="analysis_result")
    
    def __repr__(self) -> str:
        return f"<AnalysisResult {self.event_type}: {self.analyzer_name}>"
