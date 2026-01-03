"""
VNCSSDetector Web Service - Node Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from pydantic import BaseModel, Field

from app.models.node import DeviceType, NodeStatus


class NodeBase(BaseModel):
    """Base node schema."""
    name: str = Field(..., min_length=1, max_length=255)
    device_type: DeviceType
    ip_address: Optional[str] = None
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = None
    config: Optional[dict[str, Any]] = None


class NodeCreate(NodeBase):
    """Schema for creating a node."""
    pass


class NodeUpdate(BaseModel):
    """Schema for updating a node."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    device_type: Optional[DeviceType] = None
    ip_address: Optional[str] = None
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    location_lng: Optional[Decimal] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = None
    config: Optional[dict[str, Any]] = None


class NodeResponse(NodeBase):
    """Schema for node response."""
    id: int
    uuid: str
    status: NodeStatus
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NodeStats(BaseModel):
    """System stats from a node."""
    node_id: int
    node_uuid: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    is_recording: bool
    current_recording_name: Optional[str] = None
    uptime_seconds: int
    last_updated: datetime


class NodeApiKeyResponse(BaseModel):
    """Response containing node API key (only shown once)."""
    node_id: int
    uuid: str
    api_key: str
    message: str = "Store this API key securely. It will not be shown again."
