"""
VNCSSDetector Web Service - Recording Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.recording import RecordingStatus, AnalysisStatus


class RecordingBase(BaseModel):
    """Base recording schema."""
    name: str


class RecordingCreate(RecordingBase):
    """Schema for creating a recording."""
    node_id: int


class RecordingUpdate(BaseModel):
    """Schema for updating a recording."""
    status: Optional[RecordingStatus] = None
    file_size_bytes: Optional[int] = None
    stopped_at: Optional[datetime] = None
    analysis_status: Optional[AnalysisStatus] = None
    warning_count: Optional[int] = None


class RecordingResponse(RecordingBase):
    """Schema for recording response."""
    id: int
    node_id: int
    file_path: str
    file_size_bytes: int
    status: RecordingStatus
    started_at: datetime
    stopped_at: Optional[datetime] = None
    analysis_status: AnalysisStatus
    warning_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecordingWithNode(RecordingResponse):
    """Recording response with node info."""
    node_name: str
    node_uuid: str


class AnalysisResultResponse(BaseModel):
    """Schema for analysis result response."""
    id: int
    recording_id: int
    timestamp: datetime
    event_type: str
    analyzer_name: str
    message: str
    details: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
