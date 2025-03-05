from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.repositories.unit import UnitRepository
from src.schemas.unit import UnitCreate, UnitUpdate
from src.models.unit import Unit

class UnitService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repository = UnitRepository(db)
    
    async def create_unit(self, unit_data: UnitCreate) -> Unit:
        # Check if code already exists
        existing_unit: Optional[Unit] = await self._repository.get_by_code(unit_data.code)
        if existing_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit code already exists"
            )
        
        return await self._repository.create(unit_data)
    
    async def get_unit(self, unit_id: int) -> Unit:
        unit: Optional[Unit] = await self._repository.get_by_id(unit_id)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit
    
    async def get_all_units(self) -> List[Unit]:
        return await self._repository.get_all()
    
    async def update_unit(self, unit_id: int, unit_data: UnitUpdate) -> Unit:
        if unit_data.code:
            existing_unit: Optional[Unit] = await self._repository.get_by_code(unit_data.code)
            if existing_unit and existing_unit.id != unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unit code already exists"
                )
        
        unit: Optional[Unit] = await self._repository.update(unit_id, unit_data)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit
    
    async def delete_unit(self, unit_id: int) -> Dict[str, str]:
        success: bool = await self._repository.delete(unit_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return {"message": "Unit deleted successfully"}