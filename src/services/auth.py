# src/services/auth.py
from datetime import timedelta
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
import redis.asyncio as redis

from src.core.config import settings
from src.auth.security import SecurityService
from src.auth.jwt import JWTHandler
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.token import TokenResponse, GoogleTokenData
from src.services.token import TokenBlacklistService

class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        redis_client: redis.Redis = None
    ):
        self._db = db
        self._repository = UserRepository(db)
        self._security = SecurityService(db)
        self._jwt_handler = JWTHandler()
        self._blacklist = TokenBlacklistService(redis_client) if redis_client else None

    async def _prepare_token_data(self, user: User) -> dict:
        """Prepare token payload data from user"""
        # Pastikan relasi sudah diload sebelum diakses
        # Gunakan refresh untuk memastikan relasi diload dengan benar
        await self._db.refresh(user, ["roles", "unit"])
        
        # Get user roles asynchronously setelah dipastikan sudah diload
        role_data = []
        if hasattr(user, "roles") and user.roles is not None:
            role_data = [
                {
                    "id": role.id,
                    "name": role.name
                } for role in user.roles
            ]
        
        # Get user unit asynchronously
        unit_data = None
        if hasattr(user, "unit") and user.unit is not None:
            unit_data = {
                "id": user.unit.id,
                "code": user.unit.code,
                "name": user.unit.name
            }

        return {
            "sub": user.email,
            "user_id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "unit": unit_data,
            "roles": role_data,
            "first_name": user.first_name,
            "last_name": user.last_name
        }


    async def verify_google_token(self, token: str) -> GoogleTokenData:
        return await self._security.verify_google_token(token)

    async def get_or_create_user(self, user_data: GoogleTokenData) -> User:
        user = await self._repository.get_by_email(user_data.email)

        # Jika email tidak ditemukan, tolak akses
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not registered. Contact admin."
            )

        # Jika email ditemukan tetapi google_id masih kosong, update google_id
        if not user.google_id:
            user = await self._repository.update_google_id(user.id, user_data.google_id)

        return user

    async def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens with complete user data"""
        # Verify user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )

        # Prepare token data
        token_data = await self._prepare_token_data(user)
        
        # Create access token menggunakan JWTHandler
        access_token = self._jwt_handler.create_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Create refresh token - only include minimal data
        refresh_token_data = {
            "sub": user.email,
            "user_id": user.id,
            "token_type": "refresh"
        }
        refresh_token = self._jwt_handler.create_token(
            data=refresh_token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Get new access token using refresh token"""
        # Verify refresh token is not blacklisted
        if self._blacklist and await self._blacklist.is_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )

        # Decode and verify refresh token menggunakan JWTHandler
        try:
            payload = self._jwt_handler.decode_token(refresh_token)
            if payload.get("token_type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Get user and create new tokens
            user = await self._security.get_user_by_email(payload["sub"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            return await self.create_tokens(user)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )

    async def blacklist_token(self, token: str, is_refresh_token: bool = False) -> None:
        """Blacklist access or refresh token"""
        if self._blacklist:
            expires_in = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400 if is_refresh_token else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            await self._blacklist.add_to_blacklist(token, expires_in)

    async def is_token_blacklisted(self, token: str) -> bool:
        return await self._blacklist.is_blacklisted(token) if self._blacklist else False