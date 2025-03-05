from typing import Optional, List
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.models.role import Role
from src.models.unit import Unit
from src.models.user import UserRole
from src.schemas.user import UserCreate, UserUpdate, UserResponse

class UserRepository:
  def __init__(self, db: AsyncSession):
    self.db = db

  async def create(self, user_data: UserCreate) -> User:
    user = User(
      email=user_data.email,
      first_name=user_data.first_name,
      last_name=user_data.last_name,
      unit_id=user_data.unit_id,
    )
    self.db.add(user)
    await self.db.commit()
    await self.db.refresh(user)

    # Add roles
    for role_id in user_data.roles:
      user_role = UserRole(user_id=user.id, role_id=role_id)
      self.db.add(user_role)
    await self.db.commit()

    return await self.get_by_id(user.id)
  
  async def get_by_id(self, user_id: int) -> Optional[User]:
    query = select(User).options(selectinload(User.roles)).where(User.id == user_id)

    result = await self.db.exec(query)
    return result.one_or_none()
  
  async def get_by_email(self, email: str) -> Optional[User]:
    query = select(User).where(User.email == email)
    result = await self.db.exec(query)
    return result.one_or_none()
  
  async def get_all(self) -> List[User]:
    query = select(User).options(selectinload(User.roles))
    result = await self.db.exec(query)
    return result.all()
  
  async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
    user = await self.get_by_id(user_id)
    if not user:
      return None
    
    update_data = user_data.model_dump(exclude_unset=True)

    # Handle role updates if provided
    if "roles" in update_data:
      roles = update_data.pop("roles")

      # Remove existing roles
      delete_query = select(UserRole).where(UserRole.user_id == user_id)
      existing_roles = await self.db.exec(delete_query)
      for user_role in existing_roles.scalars().all():
        await self.db.delete(user_role)

      # Add new roles
      for role_id in roles:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
    
    # Update user fields
    for key, value in update_data.items():
      setattr(user, key, value)
    
    await self.db.commit()
    await self.db.refresh(user)

    return user
  
  async def delete(self, user_id: int) -> bool:
    user = await self.get_by_id(user_id)
    if not user:
      return False
    
    await self.db.delete(user)
    await self.db.commit()
    return True
  
  async def update_google_id(self, user_id: int, google_id: str) -> Optional[User]:
    user = await self.get_by_id(user_id)
    if user:
      user.google_id = google_id
      await self.db.commit()
      await self.db.refresh(user)
      return user
    return user

