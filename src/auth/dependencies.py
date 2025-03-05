from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db
from src.models.user import User
from src.auth.security import SecurityService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency for getting current authenticated user
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Dependency to get the current authenticated user"""
    security = SecurityService(db)
    return await security.verify_and_get_user(token)

# Dependency for getting current active user
async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Dependency to get the current active user"""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user

# Dependency for getting current admin user
async def get_current_admin_user(
    user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Dependency to get the current admin user"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user