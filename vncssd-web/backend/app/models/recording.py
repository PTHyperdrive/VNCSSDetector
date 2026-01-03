"""
VNCSSDetector Web Service - Recording Model
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Enum, DateTime, BigInteger, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordingStatus(str, PyEnum):
    """Recording status."""
    RECORDING = "recording"
    STOPPED = "stopped"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    ERROR = "error"


class AnalysisStatus(str, PyEnum):
    """Analysis status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Recording(Base):
    """QMDL recording model."""
    
    __tablename__ = "recordings"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[RecordingStatus] = mapped_column(
        Enum(RecordingStatus), 
        default=RecordingStatus.RECORDING, 
        index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    analysis_status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus), 
        default=AnalysisStatus.PENDING
    )
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    
    # Relationships
    node = relationship("Node", back_populates="recordings")
    analysis_results = relationship(
        "AnalysisResult", 
        back_populates="recording", 
        cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="recording")
    
    def __repr__(self) -> str:
        return f"<Recording {self.name}>"
