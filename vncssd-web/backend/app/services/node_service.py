"""
VNCSSDetector Web Service - Node Service
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node import Node, NodeStatus, DeviceType
from app.models.recording import Recording, RecordingStatus
from app.schemas.node import NodeCreate, NodeUpdate
from app.services.auth_service import AuthService


class NodeService:
    """Service for node management operations."""
    
    @staticmethod
    async def create_node(
        db: AsyncSession,
        node_data: NodeCreate
    ) -> tuple[Node, str]:
        """Create a new node and return (node, api_key)."""
        # Generate UUID and API key
        node_uuid = str(uuid.uuid4())
        api_key, api_key_hash = AuthService.generate_api_key()
        
        node = Node(
            uuid=node_uuid,
            name=node_data.name,
            device_type=node_data.device_type,
            ip_address=node_data.ip_address,
            location_lat=node_data.location_lat,
            location_lng=node_data.location_lng,
            location_name=node_data.location_name,
            config=node_data.config,
            api_key_hash=api_key_hash,
            status=NodeStatus.OFFLINE
        )
        db.add(node)
        await db.flush()
        await db.refresh(node)
        
        return node, api_key
    
    @staticmethod
    async def get_node_by_id(db: AsyncSession, node_id: int) -> Optional[Node]:
        """Get a node by ID."""
        result = await db.execute(
            select(Node).where(Node.id == node_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_node_by_uuid(db: AsyncSession, node_uuid: str) -> Optional[Node]:
        """Get a node by UUID."""
        result = await db.execute(
            select(Node).where(Node.uuid == node_uuid)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_nodes(
        db: AsyncSession,
        status: Optional[NodeStatus] = None,
        device_type: Optional[DeviceType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Node]:
        """Get all nodes with optional filtering."""
        query = select(Node)
        
        if status:
            query = query.where(Node.status == status)
        if device_type:
            query = query.where(Node.device_type == device_type)
            
        query = query.offset(skip).limit(limit).order_by(Node.name)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_node(
        db: AsyncSession,
        node: Node,
        node_data: NodeUpdate
    ) -> Node:
        """Update a node."""
        update_data = node_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(node, field, value)
        
        await db.flush()
        await db.refresh(node)
        return node
    
    @staticmethod
    async def delete_node(db: AsyncSession, node: Node) -> None:
        """Delete a node."""
        await db.delete(node)
        await db.flush()
    
    @staticmethod
    async def update_node_status(
        db: AsyncSession,
        node: Node,
        status: NodeStatus,
        ip_address: Optional[str] = None
    ) -> Node:
        """Update node status and last seen timestamp."""
        node.status = status
        node.last_seen_at = datetime.utcnow()
        
        if ip_address:
            node.ip_address = ip_address
            
        await db.flush()
        await db.refresh(node)
        return node
    
    @staticmethod
    async def regenerate_api_key(db: AsyncSession, node: Node) -> tuple[Node, str]:
        """Regenerate API key for a node."""
        api_key, api_key_hash = AuthService.generate_api_key()
        node.api_key_hash = api_key_hash
        
        await db.flush()
        await db.refresh(node)
        
        return node, api_key
    
    @staticmethod
    async def authenticate_node(
        db: AsyncSession,
        node_uuid: str,
        api_key: str
    ) -> Optional[Node]:
        """Authenticate a node by UUID and API key."""
        node = await NodeService.get_node_by_uuid(db, node_uuid)
        
        if not node or not node.api_key_hash:
            return None
            
        if not AuthService.verify_api_key(api_key, node.api_key_hash):
            return None
            
        return node
    
    @staticmethod
    async def get_node_counts(db: AsyncSession) -> dict:
        """Get node counts by status."""
        result = await db.execute(
            select(Node.status, func.count(Node.id))
            .group_by(Node.status)
        )
        
        counts = {status.value: 0 for status in NodeStatus}
        for status, count in result.all():
            counts[status.value] = count
            
        counts["total"] = sum(counts.values())
        return counts
    
    @staticmethod
    async def is_node_recording(db: AsyncSession, node_id: int) -> tuple[bool, Optional[str]]:
        """Check if a node is currently recording."""
        result = await db.execute(
            select(Recording)
            .where(Recording.node_id == node_id)
            .where(Recording.status == RecordingStatus.RECORDING)
        )
        recording = result.scalar_one_or_none()
        
        if recording:
            return True, recording.name
        return False, None
