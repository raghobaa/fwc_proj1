import asyncio
import json
import os
from pathlib import Path
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

CHAT_HISTORY_FILE = Path(__file__).resolve().parents[1] / "data" / "chat_history.json"

_lock = asyncio.Lock()

# ── helpers ──────────────────────────────────────────────────────────────────

def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or content)
    return str(content)

def _should_store(msg: BaseMessage) -> bool:
    if isinstance(msg, HumanMessage):
        return True
    if isinstance(msg, AIMessage):
        # Skip intermediate tool-call steps; keep only the final assistant reply.
        if getattr(msg, "tool_calls", None):
            return False
        return bool(msg.content)
    return False

def _serialize(msg: BaseMessage) -> dict:
    return {"role": "human" if isinstance(msg, HumanMessage) else "ai", "content": _content_to_text(msg.content)}

def _deserialize(doc: dict) -> BaseMessage:
    text = _content_to_text(doc["content"])
    if doc["role"] == "human":
        return HumanMessage(content=text)
    return AIMessage(content=text)

def _read_file() -> dict:
    if not CHAT_HISTORY_FILE.exists():
        return {}
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}

def _write_file(data: dict):
    CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── JSON-backed async functions ─────────────────────────────────────────────

async def get_chat_db(user_email: str) -> List[BaseMessage]:
    """Load chat history from the JSON file for this user."""
    async with _lock:
        data = await asyncio.to_thread(_read_file)
    messages = data.get(user_email, [])
    if not isinstance(messages, list):
        return []
    return [_deserialize(m) for m in messages if isinstance(m, dict) and "role" in m and "content" in m]

async def update_chat_db(user_email: str, messages: List[BaseMessage]):
    """Persist chat history to the JSON file, replacing the previous record."""
    serialized = [_serialize(m) for m in messages if _should_store(m)]
    async with _lock:
        data = await asyncio.to_thread(_read_file)
        data[user_email] = serialized
        await asyncio.to_thread(_write_file, data)

async def clear_chat_db(user_email: str):
    """Delete chat history for a user."""
    async with _lock:
        data = await asyncio.to_thread(_read_file)
        data.pop(user_email, None)
        await asyncio.to_thread(_write_file, data)

async def get_chat_as_display(user_email: str) -> list:
    """Return chat history as simple {role, text} dicts for the frontend."""
    async with _lock:
        data = await asyncio.to_thread(_read_file)
    messages = data.get(user_email, [])
    if not isinstance(messages, list):
        return []
    return [{"role": m["role"], "text": _content_to_text(m["content"])} for m in messages if isinstance(m, dict) and "role" in m and "content" in m]
