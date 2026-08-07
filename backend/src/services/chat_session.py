from typing import Dict, List
from langchain_core.messages import BaseMessage

# In-memory store mapping customerId to a list of messages
chat_sessions: Dict[str, List[BaseMessage]] = {}

def get_chat(customer_id: str) -> List[BaseMessage]:
    """Retrieve or create a chat session for the given customer."""
    if customer_id not in chat_sessions:
        chat_sessions[customer_id] = []
        print(f"Created new chat session for customer {customer_id}")
    return chat_sessions[customer_id]

def update_chat(customer_id: str, new_messages: List[BaseMessage]):
    """Update the chat session with new messages from the orchestrator loop."""
    # new_messages contains the system prompt at the beginning, so we just replace the whole history
    # Or, we can extract just the history excluding the system prompt.
    # The orchestrator builds the list from scratch every time it starts a turn.
    # We should only store the human and AI messages.
    chat_sessions[customer_id] = [m for m in new_messages if m.type != "system"]

def clear_chat(customer_id: str):
    if customer_id in chat_sessions:
        del chat_sessions[customer_id]

def clear_all_chats():
    chat_sessions.clear()
