"""
VNCSSDetector Web Service - Mobile Token Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database import Base


class MobileToken(Base):
    """Model for mobile app tokens."""
    
    __tablename__ = "mobile_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<MobileToken(id={self.id}, name='{self.name}', active={self.is_active})>"
