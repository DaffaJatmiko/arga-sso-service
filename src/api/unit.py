from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.services.unit import UnitService
from src.schemas.unit import UnitCreate, UnitUpdate, UnitResponse
from src.models.user import User

router = APIRouter()

@router.get("/", response_model=List[UnitResponse])
async def get_units(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get all units"""
    unit_service = UnitService(db)
    return await unit_service.get_all_units()

@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new unit (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create units"
        )
    try:
        unit_service = UnitService(db)
        return await unit_service.create_unit(unit_data)
    except Exception as e:
        print(f"Error creating unit : {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get specific unit by ID"""
    unit_service = UnitService(db)
    return await unit_service.get_unit(unit_id)

@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update unit (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update units"
        )
    unit_service = UnitService(db)
    return await unit_service.update_unit(unit_id, unit_data)

@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete unit (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete units"
        )
    unit_service = UnitService(db)
    return await unit_service.delete_unit(unit_id)