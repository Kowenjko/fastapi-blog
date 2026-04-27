from fastapi import HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.repository import UserRepository
from app.auth.schemas import Token, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.repository import AuthRepository

from app.utils.auth_utils import (
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
    create_access_token,
)
from app.core.config import settings
from datetime import UTC, datetime, timedelta

from app.utils.email_utils import send_password_reset_email


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.auth_repository = AuthRepository(session)

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm):
        # Look up user by email (case-insensitive)
        # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email

        user = await self.user_repository.get_by_email(form_data.username)

        # Verify user exists and password is correct
        # Don't reveal which one failed (security best practice)
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token with user id as subject
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type="bearer")

    async def forgot_password(
        self,
        request_data: ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
    ):
        user = await self.user_repository.get_by_email(request_data.email)
        if user:
            await self.auth_repository.delete_tokens_for_user(user.id)

        token = generate_reset_token()
        token_hash = hash_reset_token(token)

        await self.auth_repository.create_password_reset_token(
            user_id=user.id, token_hash=token_hash
        )

        await self.session.commit()

        background_tasks.add_task(
            send_password_reset_email,
            to_email=user.email,
            username=user.username,
            token=token,
        )

        return {
            "message": "If an account exists with this email, you will receive password reset instructions.",
        }

    async def reset_password(
        self,
        request_data: ResetPasswordRequest,
        session: AsyncSession,
    ):
        token_hash = hash_reset_token(request_data.token)

        reset_token = await self.auth_repository.get_valid_reset_token(token_hash)

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        if reset_token.expires_at < datetime.now(UTC):
            await self.auth_repository.delete_reset_token(reset_token)
            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user = await self.auth_repository.get_user_by_reset_token(reset_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        user.password_hash = hash_password(request_data.new_password)

        await self.auth_repository.delete_tokens_for_user(user.id)
        await session.commit()

        return {
            "message": "Password reset successfully. You can now log in with your new password.",
        }
