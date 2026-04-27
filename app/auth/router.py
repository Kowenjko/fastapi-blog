from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

from app.users.models import User

from app.auth.services import AuthService
from app.auth.schemas import ForgotPasswordRequest, Token

router = APIRouter(tags=["Auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(form_data)


@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    auth_service = AuthService(db)
    return await auth_service.forgot_password(request_data, background_tasks)
