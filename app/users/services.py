from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.posts.schemas import PaginatedPostsResponse, PostResponse
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate
from app.utils.auth_utils import CurrentUser
from app.utils.image_utils import delete_profile_image


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

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 10):
        user = await self.get_by_id(user_id)  # Ensure user exists

        total_posts = await self.repository.total_posts(user_id)
        posts = await self.repository.get_user_posts(user_id, limit=limit, skip=skip)

        has_more = skip + len(posts) < total_posts

        return PaginatedPostsResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=total_posts,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        current_user_id: int,
    ):
        await self._user_forbidden(user_id, current_user_id)
        user = await self.get_by_id(user_id)

        if (
            user_update.username is not None
            and user_update.username.lower() != user.username.lower()
        ):
            self._already_username(user_update.username)

        if (
            user_update.email is not None
            and user_update.email.lower() != user.email.lower()
        ):
            self._already_user_email(user_update.email)

        if user_update.username is not None:
            user.username = user_update.username
        if user_update.email is not None:
            user.email = user_update.email.lower()

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int, current_user_id: int):
        await self._user_forbidden(user_id, current_user_id)
        user = await self.get_by_id(user_id)
        await self.repository.delete(user)
        await self.session.commit()

        old_filename = user.image_file
        if old_filename:
            delete_profile_image(old_filename)

    # private helper methods
    async def _user_forbidden(self, user_id: int, current_user_id: int) -> bool:
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user",
            )

    async def _already_username(self, username: str):
        existing_user = await self.repository.get_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    async def _already_user_email(self, email: str):
        existing_user = await self.repository.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
