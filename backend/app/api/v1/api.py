from fastapi import APIRouter
from .endpoints import users, connections, chat, notifications

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(connections.router)
api_router.include_router(chat.router)
api_router.include_router(notifications.router)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(connections.router)
api_router.include_router(chat.router)
api_router.include_router(notifications.router)
