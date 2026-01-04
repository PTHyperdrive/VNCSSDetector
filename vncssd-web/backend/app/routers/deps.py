"""
VNCSSDetector Web Service - Authentication Dependencies
Session-based authentication using HTTP-only cookies
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.routers.auth import get_session, SESSION_COOKIE_NAME


async def get_current_user(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from session cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
    
    if not session_id:
        raise credentials_exception
    
    session = get_session(session_id)
    if not session:
        raise credentials_exception
    
    user = await AuthService.get_user_by_id(db, session["user_id"])
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user if active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(required_roles: list[UserRole]):
    """Dependency factory for role-based access control."""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {[r.value for r in required_roles]}"
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_role([UserRole.ADMIN])
require_operator = require_role([UserRole.ADMIN, UserRole.OPERATOR])
require_viewer = require_role([UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER])


async def get_optional_user(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not session_id:
        return None
    
    session = get_session(session_id)
    if not session:
        return None
    
    return await AuthService.get_user_by_id(db, session["user_id"])
