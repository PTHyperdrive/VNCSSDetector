"""
VNCSSDetector Web Service - User Model
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Boolean, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, PyEnum):
    """User roles."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]), 
        default=UserRole.VIEWER, 
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
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
    acknowledged_alerts = relationship("Alert", back_populates="acknowledged_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
