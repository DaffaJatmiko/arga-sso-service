from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis import Redis
from sqlmodel.ext.asyncio.session import AsyncSession
import redis.asyncio as redis

from src.models.user import User
from src.schemas.user import UserResponse
from src.core.database import get_db
from src.core.redis import get_redis
from src.services.auth import AuthService
from src.schemas.token import TokenResponse, TokenVerifyResponse
from src.auth.security import SecurityService
from src.auth.oauth import oauth_provider
from src.auth.dependencies import oauth2_scheme, get_current_user
from src.auth.oauth import oauth_provider


router = APIRouter()
@router.get("/login")
async def login(request: Request):
    """Start Google OAuth flow"""
    redirect_uri = request.url_for('google_oauth_callback')
    return await oauth_provider.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def google_oauth_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Handle Google OAuth callback"""
    # Get token from Google
    token = await oauth_provider.google.authorize_access_token(request)
    
    auth_service = AuthService(db, redis)
    
    # Verify token and get user info
    user_info = await auth_service.verify_google_token(token['id_token'])
    
    # Get or create user
    user = await auth_service.get_or_create_user(user_info)
    
    # Create session tokens
    return await auth_service.create_tokens(user)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[redis.Redis, Depends(get_redis)]
) -> dict[str, str]:
    """Blacklist the current access token"""
    auth_service = AuthService(db, redis)
    await auth_service.blacklist_token(token)
    return {"message": "Successfully logged out"}

@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token_endpoint(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[redis.Redis, Depends(get_redis)]
) -> TokenVerifyResponse:
    """Verify token validity"""
    auth_service = AuthService(db, redis)
    
    if await auth_service.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted"
        )
    
    return await auth_service.verify_token(token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> TokenResponse:
    """Get new access token using refresh token"""
    auth_service = AuthService(db, redis)
    return await auth_service.refresh_access_token(refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """Get current logged in user info"""
    return user


@router.post("/revoke")
async def revoke_refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Revoke refresh token"""
    auth_service = AuthService(db, redis)
    await auth_service.revoke_refresh_token(refresh_token)
    return {"message": "Token revoked successfully"}