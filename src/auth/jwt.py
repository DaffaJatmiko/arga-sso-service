from datetime import datetime, timedelta
from typing import Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status

from src.core.config import settings
from src.schemas.token import TokenPayload

class JWTHandler:
    """Handler for JWT token operations"""
    
    @staticmethod
    def create_token(data: Dict, expires_delta: timedelta) -> str:
        """Create a JWT token with expiration"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    @staticmethod
    def create_access_token(data: Dict) -> str:
        """Create an access token with standard expiration"""
        return JWTHandler.create_token(
            data=data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """Create a refresh token with standard expiration"""
        refresh_data = data.copy()
        refresh_data.update({"token_type": "refresh"})
        return JWTHandler.create_token(
            data=refresh_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )