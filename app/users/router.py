from typing import Annotated
from fastapi import APIRouter, Query, UploadFile, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

from app.posts.schemas import PaginatedPostsResponse
from app.users.services import UserService
from app.users.schemas import UserPrivate, UserCreate, UserUpdate

from app.utils.auth_utils import CurrentUser


router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("/{user_id}", response_model=UserPrivate)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user_service = UserService(db)
    return await user_service.get_by_id(user_id)


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user_service = UserService(db)
    return await user_service.create_user(user)


@router.get("/{user_id}/posts", response_model=PaginatedPostsResponse)
async def get_user_posts(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page,
):
    user_service = UserService(db)
    return await user_service.get_user_posts(user_id, skip=skip, limit=limit)


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_update, current_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    await user_service.delete_user(user_id, current_user)


@router.patch("/{user_id}/picture", response_model=UserPrivate)
async def update_profile_image(
    user_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.update_image(user_id, file, current_user)


@router.delete("/{user_id}/picture", response_model=UserPrivate)
async def delete_user_picture(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.delete_image(user_id, current_user)
