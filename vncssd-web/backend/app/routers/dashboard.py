"""
VNCSSDetector Web Service - Dashboard Router
"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import Alert, AlertSeverity
from app.models.node import Node, NodeStatus
from app.models.recording import Recording, RecordingStatus
from app.models.user import User
from app.schemas.dashboard import DashboardStats, RecentAlert, NodeMapItem
from app.routers.deps import get_current_user

router = APIRouter()


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.2f} {units[i]}"


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard statistics.
    """
    # Node counts
    total_nodes_result = await db.execute(select(func.count(Node.id)))
    total_nodes = total_nodes_result.scalar() or 0
    
    online_nodes_result = await db.execute(
        select(func.count(Node.id)).where(Node.status == NodeStatus.ONLINE)
    )
    online_nodes = online_nodes_result.scalar() or 0
    
    offline_nodes_result = await db.execute(
        select(func.count(Node.id)).where(Node.status == NodeStatus.OFFLINE)
    )
    offline_nodes = offline_nodes_result.scalar() or 0
    
    warning_nodes_result = await db.execute(
        select(func.count(Node.id)).where(Node.status == NodeStatus.WARNING)
    )
    warning_nodes = warning_nodes_result.scalar() or 0
    
    # Recording counts
    total_recordings_result = await db.execute(select(func.count(Recording.id)))
    total_recordings = total_recordings_result.scalar() or 0
    
    active_recordings_result = await db.execute(
        select(func.count(Recording.id)).where(Recording.status == RecordingStatus.RECORDING)
    )
    active_recordings = active_recordings_result.scalar() or 0
    
    # Alert counts
    total_alerts_result = await db.execute(select(func.count(Alert.id)))
    total_alerts = total_alerts_result.scalar() or 0
    
    unack_alerts_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_acknowledged == False)
    )
    unacknowledged_alerts = unack_alerts_result.scalar() or 0
    
    critical_alerts_result = await db.execute(
        select(func.count(Alert.id))
        .where(Alert.severity == AlertSeverity.CRITICAL)
        .where(Alert.is_acknowledged == False)
    )
    critical_alerts = critical_alerts_result.scalar() or 0
    
    # Warnings detected
    warnings_result = await db.execute(select(func.sum(Recording.warning_count)))
    total_warnings_detected = warnings_result.scalar() or 0
    
    # Storage used
    storage_result = await db.execute(select(func.sum(Recording.file_size_bytes)))
    storage_used_bytes = storage_result.scalar() or 0
    
    return DashboardStats(
        total_nodes=total_nodes,
        online_nodes=online_nodes,
        offline_nodes=offline_nodes,
        warning_nodes=warning_nodes,
        total_recordings=total_recordings,
        active_recordings=active_recordings,
        total_alerts=total_alerts,
        unacknowledged_alerts=unacknowledged_alerts,
        critical_alerts=critical_alerts,
        total_warnings_detected=total_warnings_detected,
        storage_used_bytes=storage_used_bytes,
        storage_used_formatted=format_bytes(storage_used_bytes)
    )


@router.get("/recent-alerts", response_model=List[RecentAlert])
async def get_recent_alerts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent alerts for the dashboard.
    """
    result = await db.execute(
        select(Alert, Node.name)
        .join(Node, Alert.node_id == Node.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    
    alerts = []
    for alert, node_name in result.all():
        alerts.append(RecentAlert(
            id=alert.id,
            node_id=alert.node_id,
            node_name=node_name,
            severity=alert.severity,
            title=alert.title,
            created_at=alert.created_at,
            is_acknowledged=alert.is_acknowledged
        ))
    
    return alerts


@router.get("/node-map", response_model=List[NodeMapItem])
async def get_node_map(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get nodes with location data for map display.
    """
    result = await db.execute(
        select(Node).where(Node.location_lat.isnot(None))
    )
    nodes = list(result.scalars().all())
    
    map_items = []
    for node in nodes:
        # Check if recording
        rec_result = await db.execute(
            select(func.count(Recording.id))
            .where(Recording.node_id == node.id)
            .where(Recording.status == RecordingStatus.RECORDING)
        )
        is_recording = (rec_result.scalar() or 0) > 0
        
        # Get warning count
        warn_result = await db.execute(
            select(func.sum(Recording.warning_count))
            .where(Recording.node_id == node.id)
        )
        warning_count = warn_result.scalar() or 0
        
        map_items.append(NodeMapItem(
            id=node.id,
            uuid=node.uuid,
            name=node.name,
            status=node.status,
            location_lat=node.location_lat,
            location_lng=node.location_lng,
            location_name=node.location_name,
            is_recording=is_recording,
            warning_count=warning_count,
            last_seen_at=node.last_seen_at
        ))
    
    return map_items


@router.get("/activity")
async def get_recent_activity(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent activity across the system.
    """
    from app.models.log import AuditLog
    
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    
    return list(result.scalars().all())
