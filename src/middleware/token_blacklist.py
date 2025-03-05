from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from src.services.token import TokenBlacklistService
from src.core.redis import get_redis

class TokenBlacklistMiddleware:
    """Middleware to check if tokens are blacklisted"""
    
    def __init__(self):
        self.redis = None
        self.blacklist_service = None
        # Public paths that don't need token validation
        self.public_paths = {
            "/auth/login", 
            "/auth/callback",
            "/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

    async def __call__(self, request: Request, call_next):
        # Skip middleware for non-authenticated routes
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Initialize redis and blacklist service if not already done
        if not self.redis:
            try:
                self.redis = await get_redis()
                self.blacklist_service = TokenBlacklistService(self.redis)
            except Exception as e:
                # Handle Redis connection errors gracefully
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"},
                )
        
        # Get token from authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return await call_next(request)  # Let the OAuth2 handler handle unauthorized access
        
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return await call_next(request)
        
        try:
            # Check if token is blacklisted
            if await self.blacklist_service.is_blacklisted(token):
                # Return proper JSONResponse instead of raising exception
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token has been revoked"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Continue processing the request
            return await call_next(request)
        except Exception as e:
            # Catch all exceptions from the blacklist check
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to validate token"},
            )