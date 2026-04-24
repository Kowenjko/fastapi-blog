from pydantic import SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.templating import Jinja2Templates


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    users: str = "/users"
    posts: str = "/posts"


class TemplatesPrefix(BaseModel):
    account: str = "/account"

    posts: str = "/posts"
    post: str = "/posts/{post_id}"
    user_posts: str = "/users/{user_id}/posts"

    login: str = "/login"
    user_register: str = "/register"
    forgot_password: str = "/forgot-password"
    reset_password: str = "/reset-password"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "FastAPI Blog"
    debug: bool = True

    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    templates: TemplatesPrefix = TemplatesPrefix()
    jinja_templates: Jinja2Templates = Jinja2Templates(
        directory="templates",
    )

    database_url: str
    frontend_url: str = "http://localhost:8000"

    static_dir: str = "static"
    media_dir: str = "media"

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024

    posts_per_page: int = 10

    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True


settings = Settings()  # type: ignore[call-arg] # Loaded from .env file
