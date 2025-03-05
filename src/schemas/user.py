from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

from .role import RoleResponse
from .unit import UnitResponse

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    unit_id: Optional[int] = None

class UserCreate(UserBase):
    roles: List[int]

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    unit_id: Optional[int] = None
    roles: Optional[List[int]] = None

class UserResponse(UserBase):
    id: int
    google_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    unit: Optional[UnitResponse] = None
    roles: List[RoleResponse] = []



