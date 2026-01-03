"""
VNCSSDetector Web Service - Routers Package
"""
from app.routers import auth, users, nodes, recordings, alerts, dashboard

__all__ = [
    "auth",
    "users",
    "nodes",
    "recordings",
    "alerts",
    "dashboard",
]
