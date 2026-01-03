"""
VNCSSDetector Web Service - Alert Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.alert import AlertSeverity


class AlertBase(BaseModel):
    """Base alert schema."""
    severity: AlertSeverity
    title: str
    description: Optional[str] = None


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    node_id: int
    recording_id: Optional[int] = None
    analysis_result_id: Optional[int] = None


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""
    is_acknowledged: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    node_id: int
    recording_id: Optional[int] = None
    analysis_result_id: Optional[int] = None
    is_acknowledged: bool
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertWithDetails(AlertResponse):
    """Alert response with related entity details."""
    node_name: str
    node_uuid: str
    recording_name: Optional[str] = None
    acknowledged_by_name: Optional[str] = None
