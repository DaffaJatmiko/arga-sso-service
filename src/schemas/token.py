from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: EmailStr
    exp: Optional[int] = None
    iat: Optional[int] = None

class TokenVerifyResponse(BaseModel):
    is_valid: bool
    payload: TokenPayload

class GoogleTokenData(BaseModel):
    email: EmailStr
    google_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None