"""
VNCSSDetector Web Service - Node Model
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, Any

from sqlalchemy import String, Enum, DateTime, Numeric, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeviceType(str, PyEnum):
    """Supported device types."""
    ORBIC = "ORBIC"
    TPLINK = "TPLINK"
    TMOBILE = "TMOBILE"
    WINGTECH = "WINGTECH"
    PINEPHONE = "PINEPHONE"
    MSM8916 = "MSM8916"
    OTHER = "OTHER"


class NodeStatus(str, PyEnum):
    """Node connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"


class Node(Base):
    """VNCSSDetector node model."""
    
    __tablename__ = "nodes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(
        Enum(DeviceType), 
        nullable=False, 
        index=True
    )
    status: Mapped[NodeStatus] = mapped_column(
        Enum(NodeStatus), 
        default=NodeStatus.OFFLINE, 
        index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    location_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    location_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8))
    location_name: Mapped[Optional[str]] = mapped_column(String(255))
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255))
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    config: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    recordings = relationship("Recording", back_populates="node", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="node", cascade="all, delete-orphan")
    system_logs = relationship("SystemLog", back_populates="node", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Node {self.name} ({self.uuid})>"
