"""
VNCSSDetector Web Service - Alerts Router
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import Alert, AlertSeverity
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertWithDetails
from app.routers.deps import get_current_user, require_operator

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    node_id: Optional[int] = None,
    severity: Optional[AlertSeverity] = None,
    is_acknowledged: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all alerts with optional filtering.
    """
    query = select(Alert)
    
    if node_id:
        query = query.where(Alert.node_id == node_id)
    if severity:
        query = query.where(Alert.severity == severity)
    if is_acknowledged is not None:
        query = query.where(Alert.is_acknowledged == is_acknowledged)
    
    query = query.offset(skip).limit(limit).order_by(Alert.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/unacknowledged/count")
async def get_unacknowledged_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unacknowledged alerts by severity.
    """
    result = await db.execute(
        select(Alert.severity, func.count(Alert.id))
        .where(Alert.is_acknowledged == False)
        .group_by(Alert.severity)
    )
    
    counts = {s.value: 0 for s in AlertSeverity}
    for severity, count in result.all():
        counts[severity.value] = count
    
    counts["total"] = sum(counts.values())
    return counts


@router.get("/{alert_id}", response_model=AlertWithDetails)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific alert by ID with related details.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Get related entity names
    from app.models.node import Node
    from app.models.recording import Recording
    
    node_result = await db.execute(
        select(Node).where(Node.id == alert.node_id)
    )
    node = node_result.scalar_one_or_none()
    
    recording_name = None
    if alert.recording_id:
        rec_result = await db.execute(
            select(Recording).where(Recording.id == alert.recording_id)
        )
        recording = rec_result.scalar_one_or_none()
        if recording:
            recording_name = recording.name
    
    acknowledged_by_name = None
    if alert.acknowledged_by_id:
        from app.models.user import User as UserModel
        user_result = await db.execute(
            select(UserModel).where(UserModel.id == alert.acknowledged_by_id)
        )
        ack_user = user_result.scalar_one_or_none()
        if ack_user:
            acknowledged_by_name = ack_user.full_name or ack_user.email
    
    return AlertWithDetails(
        **alert.__dict__,
        node_name=node.name if node else "Unknown",
        node_uuid=node.uuid if node else "Unknown",
        recording_name=recording_name,
        acknowledged_by_name=acknowledged_by_name
    )


@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Acknowledge an alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.is_acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert is already acknowledged"
        )
    
    alert.is_acknowledged = True
    alert.acknowledged_by_id = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(alert)
    
    return alert


@router.put("/acknowledge-all")
async def acknowledge_all_alerts(
    node_id: Optional[int] = None,
    severity: Optional[AlertSeverity] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Acknowledge all matching alerts.
    """
    query = select(Alert).where(Alert.is_acknowledged == False)
    
    if node_id:
        query = query.where(Alert.node_id == node_id)
    if severity:
        query = query.where(Alert.severity == severity)
    
    result = await db.execute(query)
    alerts = list(result.scalars().all())
    
    now = datetime.utcnow()
    for alert in alerts:
        alert.is_acknowledged = True
        alert.acknowledged_by_id = current_user.id
        alert.acknowledged_at = now
    
    await db.flush()
    
    return {"acknowledged_count": len(alerts)}


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Dismiss (delete) an alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    await db.delete(alert)
    await db.flush()
