"""
VNCSSDetector Web Service - Schemas Package
"""
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserInDB,
    Token, TokenData, LoginRequest
)
from app.schemas.node import (
    NodeCreate, NodeUpdate, NodeResponse, NodeStats
)
from app.schemas.recording import (
    RecordingCreate, RecordingUpdate, RecordingResponse
)
from app.schemas.alert import (
    AlertCreate, AlertUpdate, AlertResponse
)
from app.schemas.dashboard import (
    DashboardStats, RecentAlert, NodeMapItem
)

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    "Token", "TokenData", "LoginRequest",
    # Node
    "NodeCreate", "NodeUpdate", "NodeResponse", "NodeStats",
    # Recording
    "RecordingCreate", "RecordingUpdate", "RecordingResponse",
    # Alert
    "AlertCreate", "AlertUpdate", "AlertResponse",
    # Dashboard
    "DashboardStats", "RecentAlert", "NodeMapItem",
]
