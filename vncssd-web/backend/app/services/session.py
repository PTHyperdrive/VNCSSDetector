"""
VNCSSDetector Web Service - Session Management
Shared session storage for authentication
"""
from typing import Optional
from datetime import datetime, timedelta
import secrets

# In-memory session store (use Redis in production)
sessions: dict[str, dict] = {}

SESSION_COOKIE_NAME = "vncssd_session"
SESSION_MAX_AGE = 86400 * 7  # 7 days


def create_session(user_id: int, email: str, role: str) -> str:
    """Create a new session and return the session ID."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(seconds=SESSION_MAX_AGE)).isoformat()
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Get session data by session ID."""
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    expires_at = datetime.fromisoformat(session["expires_at"])
    
    if datetime.utcnow() > expires_at:
        del sessions[session_id]
        return None
    
    return session


def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
