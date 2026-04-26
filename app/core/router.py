from fastapi import APIRouter
from app.core.config import settings

from app.users import router as user_router

router = APIRouter(prefix=settings.api.prefix)

router.include_router(user_router.router, prefix=settings.api.users)
