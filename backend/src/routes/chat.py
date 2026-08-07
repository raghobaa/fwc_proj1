from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional

from src.tools.order_tool import get_order
from src.services.agent import run_orchestrator
from src.services.chat_session import get_chat, update_chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    customerId: Optional[str] = "C-100" # Default for testing

@router.get("/test-order/{order_id}")
async def test_order(order_id: str, customerId: str = Query(...)):
    result = get_order(order_id, customerId)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result)
    return result.get("order")

@router.post("")
async def chat_no_slash(request: ChatRequest):
    return await chat(request)

@router.post("/")
async def chat(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
        
    try:
        # Get chat history
        chat_history = get_chat(request.customerId)
        
        # Run agent
        response_text, new_messages = await run_orchestrator(
            request.message, 
            request.customerId, 
            chat_history
        )
        
        # Save updated history
        update_chat(request.customerId, new_messages)
        
        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
