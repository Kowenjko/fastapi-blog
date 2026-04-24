from fastapi import Request, APIRouter
from app.core.config import settings


router = APIRouter()


@router.get(settings.templates.login, include_in_schema=False)
async def login_page(request: Request):
    return settings.jinja_templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@router.get(settings.templates.user_register, include_in_schema=False)
async def register_page(request: Request):
    return settings.jinja_templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )


@router.get(settings.templates.forgot_password, include_in_schema=False)
async def forgot_password_page(request: Request):
    return settings.jinja_templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )


@router.get(settings.templates.reset_password, include_in_schema=False)
async def reset_password_page(request: Request):
    response = settings.jinja_templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
