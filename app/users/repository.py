from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate

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

    async def update(self, user: User, data: UserUpdate):
        pass
