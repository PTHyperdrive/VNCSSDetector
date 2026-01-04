"""
VNCSSDetector Web Service - Authentication Router
Session-based authentication using HTTP-only cookies
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.services.session import (
    create_session, get_session, delete_session,
    SESSION_COOKIE_NAME, SESSION_MAX_AGE
)

router = APIRouter()


@router.post("/login")
async def login(
    login_data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password. Sets HTTP-only session cookie.
    """
    user = await AuthService.authenticate_user(
        db, 
        login_data.email, 
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create session
    session_id = create_session(user.id, user.email, user.role.value)
    
    # Set HTTP-only cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
):
    """
    Get information about the currently authenticated user.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )
    
    user = await AuthService.get_user_by_id(db, session["user_id"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    """
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await AuthService.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    return user


@router.post("/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
):
    """
    Logout the current user. Clears the session cookie.
    """
    if session_id:
        delete_session(session_id)
    
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    
    return {"success": True, "message": "Successfully logged out"}


@router.get("/check")
async def check_auth(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if the current session is valid.
    """
    if not session_id:
        return {"authenticated": False}
    
    session = get_session(session_id)
    if not session:
        return {"authenticated": False}
    
    user = await AuthService.get_user_by_id(db, session["user_id"])
    if not user or not user.is_active:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }
