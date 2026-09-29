from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional

from src.tools.order_tool import get_order, get_customer_id_by_email
from src.services.agent import run_orchestrator
from src.services.chat_session import (
    get_chat_db,
    update_chat_db,
    clear_chat_db,
    get_chat_as_display,
)
from src.config.auth import get_current_user, TokenData

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    customerId: Optional[str] = "C-101"  # kept for agent context; auth uses JWT email

# ── History endpoint ─────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(current_user: TokenData = Depends(get_current_user)):
    """Return this user's full chat history as display-friendly messages."""
    try:
        history = await get_chat_as_display(current_user.username)
        return {"messages": history}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def delete_history(current_user: TokenData = Depends(get_current_user)):
    """Clear chat history for the logged-in user."""
    await clear_chat_db(current_user.username)
    return {"detail": "History cleared"}

# ── Test order endpoint ───────────────────────────────────────────────────────

@router.get("/test-order/{order_id}")
async def test_order(order_id: str, customerId: str = Query(...)):
    result = get_order(order_id, customerId)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail=result)
    return result.get("order")

# ── Chat endpoint ─────────────────────────────────────────────────────────────

@router.post("")
async def chat_no_slash(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
):
    return await _handle_chat(request, current_user)

@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
):
    return await _handle_chat(request, current_user)

async def _handle_chat(request: ChatRequest, current_user: TokenData):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    try:
        # Load history from JSON file for this user
        chat_history = await get_chat_db(current_user.username)

        # Resolve the customer ID from the authenticated email (fall back to request value)
        customer_id = get_customer_id_by_email(current_user.username) or request.customerId

        # Run agent
        response_text, new_messages = await run_orchestrator(
            request.message,
            customer_id,
            chat_history,
            user_role=current_user.role,
            user_email=current_user.username,
        )


        # Persist updated history back to MongoDB
        await update_chat_db(current_user.username, new_messages)

        return {"response": response_text}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
