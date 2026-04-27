from typing import Annotated
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

from app.users.services import UserService
from app.users.schemas import UserPrivate, UserCreate

from app.utils.auth_utils import CurrentUser


router = APIRouter(tags=["Users"])


@router.post("/", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user_service = UserService(db)
    return await user_service.create_user(user)


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user
