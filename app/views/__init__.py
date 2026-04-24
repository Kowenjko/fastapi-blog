from fastapi import APIRouter

router = APIRouter()

from .auth import router as auth_router
from .posts import router as posts_router
from .users import router as users_router

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(posts_router)
