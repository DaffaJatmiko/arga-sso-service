from typing import Optional
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.models.user import User
from src.schemas.token import GoogleTokenData
from src.auth.jwt import JWTHandler

class SecurityService:
    """Service for security operations"""
    
    def __init__(self, db: AsyncSession):
        self._db = db
        self._jwt_handler = JWTHandler()

    @staticmethod
    async def verify_google_token(token: str) -> GoogleTokenData:
        """Verify Google OAuth token and extract user data"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
                
            return GoogleTokenData(
                email=idinfo['email'],
                google_id=idinfo['sub'],
                first_name=idinfo.get('given_name'),
                last_name=idinfo.get('family_name')
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from database, including roles"""
        query = select(User).where(User.email == email).options(selectinload(User.roles))
        result = await self._db.exec(query)
        return result.first()

    async def verify_and_get_user(self, token: str) -> User:
        """Verify token and return corresponding user"""
        payload = self._jwt_handler.decode_token(token)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await self._db.refresh(user)
        
        return user