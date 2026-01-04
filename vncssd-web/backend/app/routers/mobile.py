"""
VNCSSDetector Web Service - Mobile Token Router
"""
from typing import Optional
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.mobile_token import MobileToken
from app.services.session import get_session, SESSION_COOKIE_NAME


router = APIRouter()


class CreateTokenRequest(BaseModel):
    name: str


class TokenResponse(BaseModel):
    id: int
    token: str
    name: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class CreateTokenResponse(BaseModel):
    id: int
    token: str
    name: str
    message: str


async def get_current_session(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> dict:
    """Verify session for mobile token endpoints."""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    return session


@router.get("/tokens", response_model=list[TokenResponse])
async def list_tokens(
    session: dict = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """List all mobile tokens."""
    result = await db.execute(
        select(MobileToken).order_by(MobileToken.created_at.desc())
    )
    return result.scalars().all()


@router.post("/tokens", response_model=CreateTokenResponse)
async def create_token(
    data: CreateTokenRequest,
    session: dict = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Create a new mobile token."""
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    mobile_token = MobileToken(
        token=token,
        name=data.name,
        is_active=True
    )
    
    db.add(mobile_token)
    await db.commit()
    await db.refresh(mobile_token)
    
    return CreateTokenResponse(
        id=mobile_token.id,
        token=token,
        name=mobile_token.name,
        message="Token created successfully. Save it now - it won't be shown again!"
    )


@router.delete("/tokens/{token_id}")
async def revoke_token(
    token_id: int,
    session: dict = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Revoke (deactivate) a mobile token."""
    result = await db.execute(
        select(MobileToken).where(MobileToken.id == token_id)
    )
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    token.is_active = False
    await db.commit()
    
    return {"message": "Token revoked successfully"}


@router.post("/verify")
async def verify_mobile_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a mobile token and update last_used_at.
    Used by mobile app to verify connection.
    """
    result = await db.execute(
        select(MobileToken).where(
            MobileToken.token == token,
            MobileToken.is_active == True
        )
    )
    mobile_token = result.scalar_one_or_none()
    
    if not mobile_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token"
        )
    
    # Update last used
    mobile_token.last_used_at = datetime.utcnow()
    await db.commit()
    
    return {
        "valid": True,
        "name": mobile_token.name
    }
