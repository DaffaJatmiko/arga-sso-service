from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.role import Role
from src.models.user import UserRole
from src.schemas.role import RoleCreate, RoleUpdate

class RoleRepository:
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def create(self, role_data: RoleCreate) -> Role:
        role = Role(**role_data.model_dump())
        self._db.add(role)
        await self._db.commit()
        await self._db.refresh(role)
        return role
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        query = select(Role).where(Role.id == role_id)
        result = await self._db.exec(query)
        return result.first()
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(Role).where(Role.name == name)
        result = await self._db.exec(query)
        return result.first()
    
    async def get_all(self) -> List[Role]:
        query = select(Role)
        result = await self._db.exec(query)
        return result.all()
    
    async def update(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        role = await self.get_by_id(role_id)
        if not role:
            return None
            
        update_data = role_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)
            
        await self._db.commit()
        await self._db.refresh(role)
        return role
    
    async def delete(self, role_id: int) -> bool:
        role = await self.get_by_id(role_id)
        if not role:
            return False
            
        # Delete all UserRole associations first
        query = select(UserRole).where(UserRole.role_id == role_id)
        results = await self._db.exec(query)
        for user_role in results.all():
            await self._db.delete(user_role)
            
        await self._db.delete(role)
        await self._db.commit()
        return True

    async def get_user_roles(self, user_id: int) -> List[Role]:
        query = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        result = await self._db.execute(query)
        return result.all()