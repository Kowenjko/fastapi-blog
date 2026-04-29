from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.posts.models import Post


class PostRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_by_author(self, post_id: int):
        result = await self.session.execute(
            select(Post).options(selectinload(Post.author)).where(Post.id == post_id),
        )
        return result.scalars().first()

    async def get_by_id(self, post_id: int):
        result = await self.session.execute(
            select(Post).where(Post.id == post_id),
        )
        return result.scalars().first()

    async def create(self, post: Post):
        self.session.add(post)
        try:
            await self.session.flush()
        except Exception:
            await self.session.rollback()
            raise
        return post

    async def get_posts(self, limit: int = 10, skip: int = 0):
        result = await self.session.execute(
            select(Post)
            .options(selectinload(Post.author))
            .order_by(Post.date_posted.desc())
            .offset(skip)
            .limit(limit),
        )
        return result.scalars().all()

    async def total_posts(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Post),
        )
        return result.scalar() or 0

    async def delete(self, post: Post):
        await self.session.delete(post)
        try:
            await self.session.flush()
        except Exception:
            await self.session.rollback()
            raise
