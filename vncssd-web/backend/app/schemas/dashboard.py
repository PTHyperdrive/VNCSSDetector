"""
VNCSSDetector Web Service - Dashboard Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.alert import AlertSeverity
from app.models.node import NodeStatus


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_nodes: int
    online_nodes: int
    offline_nodes: int
    warning_nodes: int
    total_recordings: int
    active_recordings: int
    total_alerts: int
    unacknowledged_alerts: int
    critical_alerts: int
    total_warnings_detected: int
    storage_used_bytes: int
    storage_used_formatted: str


class RecentAlert(BaseModel):
    """Recent alert for dashboard."""
    id: int
    node_id: int
    node_name: str
    severity: AlertSeverity
    title: str
    created_at: datetime
    is_acknowledged: bool


class NodeMapItem(BaseModel):
    """Node item for map display."""
    id: int
    uuid: str
    name: str
    status: NodeStatus
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    location_name: Optional[str] = None
    is_recording: bool
    warning_count: int
    last_seen_at: Optional[datetime] = None


class TimeSeriesDataPoint(BaseModel):
    """Data point for time series charts."""
    timestamp: datetime
    value: float
    label: Optional[str] = None


class NodeStatusHistory(BaseModel):
    """Historical status for a node."""
    node_id: int
    node_name: str
    status_changes: list[TimeSeriesDataPoint]
    warning_counts: list[TimeSeriesDataPoint]
