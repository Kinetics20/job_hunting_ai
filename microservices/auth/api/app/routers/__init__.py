from fastapi import APIRouter

from app.routers.user import router as user_router
from app.routers.debug import router as debug_router

routers: list[APIRouter] = [
    user_router,
    debug_router,
]