from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Column, DateTime, Relationship

from src.models.user_role import UserRole

# Use TYPE_CHECKING for type hints without importing at runtime
if TYPE_CHECKING:
    from src.models.unit import Unit
    from src.models.role import Role



class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    first_name: str
    last_name: str | None = Field(default=None, nullable=True)
    google_id: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    unit_id: Optional[int] = Field(default=None, foreign_key="units.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow))

    # Relationship
    unit: Optional["Unit"] = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole)

