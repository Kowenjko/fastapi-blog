from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate

from app.posts.models import Post

from app.utils.auth_utils import hash_password


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(func.lower(User.email) == email.lower()),
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int):
        result = await self.session.execute(
            select(User).where(User.id == user_id),
        )
        return result.scalars().first()

    async def get_by_username(self, username: str):
        result = await self.session.execute(
            select(User).where(
                func.lower(User.username) == username.lower(),
            ),
        )
        return result.scalars().first()

    async def create(self, user: UserCreate):
        new_user = User(
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

    async def get_user_posts(self, user_id: int, limit: int = 10, skip: int = 0):
        result = await self.session.execute(
            select(Post)
            .options(selectinload(Post.author))
            .where(Post.user_id == user_id)
            .order_by(Post.date_posted.desc())
            .offset(skip)
            .limit(limit),
        )
        return result.scalars().all()

    async def total_posts(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(Post.user_id == user_id),
        )
        return result.scalar() or 0
