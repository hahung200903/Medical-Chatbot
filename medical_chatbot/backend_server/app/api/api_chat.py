from app.schemas.sche_chat import ChatRequest, ChatResponse, HealthResponse, FeedbackRequest
from app.services.ser_chat import ChatService
from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime

router = APIRouter()
active_conversations = {}

@router.get("", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, background_tasks: BackgroundTasks):
    service = ChatService(req.query, req.conversation_id)
    try:
        answer = service.chat()
        if answer.get("needs_feedback"):
            active_conversations[req.conversation_id] = {
                "state": answer["state"],
                "timestamp": datetime.now()
            }
            return ChatResponse(
                answer= answer["response"],
                sources= answer.get("metadata"),
                needs_feedback= answer.get("needs_feedback", False),
                cached= req.use_cache
            )
        else:
            return ChatResponse(
                answer= answer["response"],
                sources= answer.get("metadata"),
                needs_feedback= answer.get("needs_feedback", False),
                cached= req.use_cache
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/feedback", response_model=ChatResponse)
async def feedback(req: FeedbackRequest):
    if req.conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    service = ChatService(req.user_feedback, req.conversation_id)
    result = service.resume_with_feedback(req.user_feedback)

    if not result.get("needs_feedback"):
        del active_conversations[req.conversation_id]

    return {
        "answer": result["response"],
        "sources": result.get("metadata"),
        "needs_feedback": result.get("needs_feedback", False),
        "cached": False
    }