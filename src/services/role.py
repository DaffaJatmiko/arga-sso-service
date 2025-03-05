from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.repositories.role import RoleRepository
from src.schemas.role import RoleCreate, RoleUpdate
from src.models.role import Role

class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repository = RoleRepository(db)
    
    async def create_role(self, role_data: RoleCreate) -> Role:
        # Check if name already exists
        existing_role: Optional[Role] = await self._repository.get_by_name(role_data.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        
        return await self._repository.create(role_data)
    
    async def get_role(self, role_id: int) -> Role:
        role: Optional[Role] = await self._repository.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    
    async def get_all_roles(self) -> List[Role]:
        return await self._repository.get_all()
    
    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        if role_data.name:
            existing_role: Optional[Role] = await self._repository.get_by_name(role_data.name)
            if existing_role and existing_role.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role name already exists"
                )
        
        role: Optional[Role] = await self._repository.update(role_id, role_data)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    
    async def delete_role(self, role_id: int) -> Dict[str, str]:
        success: bool = await self._repository.delete(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return {"message": "Role deleted successfully"}

    async def get_user_roles(self, user_id: int) -> List[Role]:
        return await self._repository.get_user_roles(user_id)