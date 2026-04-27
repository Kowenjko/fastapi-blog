from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import PasswordResetToken
from app.users.schemas import UserCreate, UserUpdate

from app.utils.auth_utils import hash_password
from app.core.config import settings


class AuthRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_tokens_for_user(self, user_id: int):
        await self.session.execute(
            sql_delete(PasswordResetToken).where(
                func.lower(PasswordResetToken.user_id) == user_id.lower()
            )
        )

    async def create_password_reset_token(self, user_id: int, token_hash: str):
        expires_at = datetime.now(UTC) + timedelta(
            minutes=settings.reset_token_expire_minutes,
        )
        reset_token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.session.add(reset_token)
        try:
            await self.session.flush()
        except Exception:
            await self.session.rollback()
            raise
        return reset_token
