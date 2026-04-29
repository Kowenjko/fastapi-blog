from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.core.models

from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles


from starlette.exceptions import HTTPException as StarletteHTTPException

from app.views.handler import (
    general_http_exception_handler,
    validation_exception_handler,
)


from app.core.database import engine

from app.views import router as router_views
from app.core.router import router as api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


app.include_router(router_views)
app.include_router(api_router)


app.add_exception_handler(StarletteHTTPException, general_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
