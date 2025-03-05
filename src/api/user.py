from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_db
from src.services.user import UserService
from src.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
  user_data: UserCreate,
  db: AsyncSession = Depends(get_db)
):
  """Create a new user"""
  user_service = UserService(db)
  return await user_service.create_user(user_data)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Get all registered users"""
    user_service = UserService(db)
    return await user_service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific user by ID"""
    user_service = UserService(db)
    return await user_service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user"""
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete user"""
    user_service = UserService(db)
    return await user_service.delete_user(user_id)