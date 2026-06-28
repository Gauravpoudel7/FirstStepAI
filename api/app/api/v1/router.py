"""v1 API aggregator."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    chat,
    conversations,
    dashboard,
    documents,
    profile,
    projects,
    settings,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(dashboard.router)
api_router.include_router(documents.router)
api_router.include_router(profile.router)
api_router.include_router(projects.router)
api_router.include_router(settings.router)
api_router.include_router(admin.router)