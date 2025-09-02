from fastapi import APIRouter
from .endpoints import users, connections

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(connections.router)
