from fastapi import APIRouter

from app.modules.assistant.api.router import router as assistant_router
from app.modules.documents.api.router import router as documents_router
from app.modules.users.api.router import router as users_router
from app.modules.operations.api.router import router as operations_router

def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(users_router)
    router.include_router(documents_router)
    router.include_router(assistant_router)
    router.include_router(operations_router)
    return router
