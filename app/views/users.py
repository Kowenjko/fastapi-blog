from fastapi import APIRouter, Request

from app.core.config import settings


router = APIRouter()


@router.get(settings.templates.account, include_in_schema=False)
async def account_page(request: Request):
    return settings.jinja_templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )
