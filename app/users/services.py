from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.repository import UserRepository
from app.users.schemas import UserCreate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def get_by_id(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def create_user(self, user_data: UserCreate):
        existing_user = await self.repository.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        new_user = await self.repository.create(user_data)
        await self.session.commit()
        return new_user
