from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UnitBase(BaseModel):
    name: str
    code: str

class UnitCreate(UnitBase):
    pass

class UnitResponse(UnitBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UnitUpdate(UnitBase):
    name: Optional[str] = None
    code: Optional[str] = None
  

