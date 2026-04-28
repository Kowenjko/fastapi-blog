from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.posts.models import Post
from app.posts.repository import PostRepository
from app.posts.schemas import PaginatedPostsResponse, PostCreate, PostResponse
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate
from app.utils.auth_utils import CurrentUser
from app.utils.image_utils import delete_profile_image, process_profile_image

from app.core.config import settings

from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PostRepository(session)

    async def get_posts(self, skip: int = 0, limit: int = 10):
        total_posts = await self.repository.total_posts()
        posts = await self.repository.get_posts(limit=limit, skip=skip)

        has_more = skip + len(posts) < total_posts

        return PaginatedPostsResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=total_posts,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    async def get_by_id(self, post_id: int):
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        return post

    async def get_by_id_by_author(self, post_id: int):
        post = await self.repository.get_by_id_by_author(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
        return post

    async def create_post(self, post_data: PostCreate, author_id: int):
        new_post = await self.repository.create(
            Post(**post_data.model_dump(), user_id=author_id)
        )
        await self.session.commit()
        await self.session.refresh(new_post, attribute_names=["author"])
        return new_post

    async def update_post_full(
        self, post_id: int, post_data: PostCreate, current_user_id: int
    ):
        post = await self.get_by_id(post_id)
        await self._user_forbidden(post.user_id, current_user_id)

        post.title = post_data.title
        post.content = post_data.content

        await self.session.commit()
        await self.session.refresh(post, attribute_names=["author"])
        return post

    async def update_post(
        self, post_id: int, post_data: PostCreate, current_user_id: int
    ):
        post = await self.get_by_id(post_id)
        await self._user_forbidden(post.user_id, current_user_id)

        update_data = post_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        await self.session.commit()
        await self.session.refresh(post, attribute_names=["author"])
        return post

    async def delete_post(self, post_id: int, current_user_id: int):
        post = await self.get_by_id(post_id)
        await self._user_forbidden(post.user_id, current_user_id)

        await self.repository.delete(post)
        await self.session.commit()

    # private helper methods
    async def _user_forbidden(self, user_id: int, current_user_id: int) -> bool:
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user",
            )
