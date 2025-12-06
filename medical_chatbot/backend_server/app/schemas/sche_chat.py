from pydantic import BaseModel
from typing import Optional, List
import uuid

conversation_id_default = str(uuid.uuid4())

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = conversation_id_default
    use_cache: Optional[bool] = False

class ChatResponse(BaseModel):
    answer: str
    sources: dict
    needs_feedback: bool
    cached: bool

class HealthResponse(BaseModel):
    status: str
    version: str

class FeedbackRequest(BaseModel):
    conversation_id: Optional[str] = conversation_id_default
    user_feedback: Optional[str] = None
