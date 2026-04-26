from sqlalchemy.ext.asyncio import AsyncSession

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from PIL import UnidentifiedImageError
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.concurrency import run_in_threadpool

import models
from auth import (
    CurrentUser,
    create_access_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from config import settings
from database import get_db
from email_utils import send_password_reset_email
from image_utils import delete_profile_image, process_profile_image
from schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    PaginatedPostsResponse,
    PostResponse,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserPrivate,
    UserPublic,
    UserUpdate,
)


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(models.User).where(func.lower(models.User.email) == email.lower()),
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int):
        result = await self.session.execute(
            select(models.User).where(models.User.id == user_id),
        )
        return result.scalars().first()

    async def get_by_username(self, username: str):
        result = await self.session.execute(
            select(models.User).where(
                func.lower(models.User.username) == username.lower(),
            ),
        )
        return result.scalars().first()

    async def create(self, user: UserCreate):
        new_user = models.User(
            username=user.username,
            email=user.email.strip().lower(),
            password_hash=hash_password(user.password),
        )

        self.session.add(new_user)

        try:
            await self.session.flush()
        except Exception:
            await self.session.rollback()
            raise

        return new_user
