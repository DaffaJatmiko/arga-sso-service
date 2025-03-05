from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional, Dict

from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.repositories.user import UserRepository

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._repository = UserRepository(db)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        existing_user = await self._repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        return await self._repository.create(user_data)

    async def get_user(self, user_id: int) -> UserResponse:
        """Retrieve a user by their ID."""
        user = await self._repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
        
    async def get_all_users(self) -> List[UserResponse]:
        """Retrieve all users."""
        return await self._repository.get_all()
        
    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update an existing user."""
        user = await self._repository.update(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
        
    async def delete_user(self, user_id: int) -> Dict[str, str]:
        """Delete a user by ID."""
        success = await self._repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}