"""
schemas/chat.py — The contract between the chat UI and POST /chat.
"""
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, examples=["Create a task called Learn Agentic AI"])
    # Lets the agent remember earlier turns ("delete THAT task").
    conversation_id: str | None = None


class ToolCallInfo(BaseModel):
    """One tool call the agent made — returned so the UI can show 'what the agent did'."""

    tool_name: str
    args: dict[str, Any]
    status: Literal["success", "error"]
    result: Any = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tool_calls: list[ToolCallInfo] = []
