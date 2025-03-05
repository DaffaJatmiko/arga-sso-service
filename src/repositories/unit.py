from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.unit import Unit
from src.schemas.unit import UnitCreate, UnitUpdate

class UnitRepository:
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def create(self, unit_data: UnitCreate) -> Unit:
        unit = Unit(**unit_data.model_dump())
        self._db.add(unit)
        await self._db.commit()
        await self._db.refresh(unit)
        return unit
    
    async def get_by_id(self, unit_id: int) -> Optional[Unit]:
        query = select(Unit).where(Unit.id == unit_id)
        result = await self._db.exec(query)
        return result.first()
    
    async def get_by_code(self, code: str) -> Optional[Unit]:
        query = select(Unit).where(Unit.code == code)
        result = await self._db.exec(query)
        return result.first()
    
    async def get_all(self) -> List[Unit]:
        query = select(Unit)
        result = await self._db.exec(query)
        return result.all()
    
    async def update(self, unit_id: int, unit_data: UnitUpdate) -> Optional[Unit]:
        unit = await self.get_by_id(unit_id)
        if not unit:
            return None
            
        update_data = unit_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)
            
        await self._db.commit()
        await self._db.refresh(unit)
        return unit
    
    async def delete(self, unit_id: int) -> bool:
        unit = await self.get_by_id(unit_id)
        if not unit:
            return False
            
        await self._db.delete(unit)
        await self._db.commit()
        return True