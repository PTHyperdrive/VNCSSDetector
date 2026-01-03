"""
VNCSSDetector Web Service - Nodes Router
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.node import DeviceType, NodeStatus
from app.models.user import User
from app.schemas.node import (
    NodeCreate, NodeUpdate, NodeResponse, NodeStats, NodeApiKeyResponse
)
from app.services.node_service import NodeService
from app.routers.deps import get_current_user, require_operator, require_admin

router = APIRouter()


@router.get("", response_model=List[NodeResponse])
async def list_nodes(
    status: Optional[NodeStatus] = None,
    device_type: Optional[DeviceType] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all VNCSSDetector nodes.
    """
    nodes = await NodeService.get_all_nodes(
        db,
        status=status,
        device_type=device_type,
        skip=skip,
        limit=limit
    )
    return nodes


@router.post("", response_model=NodeApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Register a new VNCSSDetector node.
    Returns the API key which should be stored securely.
    """
    node, api_key = await NodeService.create_node(db, node_data)
    
    return NodeApiKeyResponse(
        node_id=node.id,
        uuid=node.uuid,
        api_key=api_key
    )


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific node by ID.
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    return node


@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: int,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Update a node's configuration.
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    updated_node = await NodeService.update_node(db, node, node_data)
    return updated_node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a node and all its recordings (admin only).
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    await NodeService.delete_node(db, node)


@router.post("/{node_id}/regenerate-key", response_model=NodeApiKeyResponse)
async def regenerate_api_key(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Regenerate the API key for a node (admin only).
    The old key will be invalidated immediately.
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    updated_node, api_key = await NodeService.regenerate_api_key(db, node)
    
    return NodeApiKeyResponse(
        node_id=updated_node.id,
        uuid=updated_node.uuid,
        api_key=api_key
    )


@router.get("/{node_id}/stats", response_model=NodeStats)
async def get_node_stats(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system stats for a node.
    Note: In production, this would fetch real-time data from the node via WebSocket.
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    is_recording, recording_name = await NodeService.is_node_recording(db, node_id)
    
    # Return placeholder stats - in production, this comes from the node
    from datetime import datetime
    return NodeStats(
        node_id=node.id,
        node_uuid=node.uuid,
        cpu_usage=0.0,
        memory_usage=0.0,
        disk_usage=0.0,
        battery_level=None,
        signal_strength=None,
        is_recording=is_recording,
        current_recording_name=recording_name,
        uptime_seconds=0,
        last_updated=datetime.utcnow()
    )


@router.get("/counts/by-status")
async def get_node_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get node counts grouped by status.
    """
    counts = await NodeService.get_node_counts(db)
    return counts
