from fastapi import APIRouter
from app.api import api_chat

router = APIRouter()
router.include_router(api_chat.router, tags=['Chat'], prefix='/chat')