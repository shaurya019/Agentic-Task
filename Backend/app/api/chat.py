"""
api/chat.py — POST /chat: the single entry point the chat UI talks to.

Responsibilities: validate the request (ChatRequest), load conversation history,
call the agent, translate failures into clean HTTP errors, return ChatResponse.
It does NOT contain business logic — that lives in the agent, tools and service.
"""
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UnexpectedModelBehavior, UsageLimitExceeded
from pydantic_ai.messages import ModelMessage
from sqlalchemy.orm import Session

from app.agents.task_agent import run_task_agent
from app.database.database import get_db
from app.logger import logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.task_service import DatabaseError
from app.tools.task_tools import AgentDeps

router = APIRouter(tags=["chat"])

# In-memory conversation memory: {conversation_id: [messages...]}.
# Simple for learning; it's lost on restart. Use a database/Redis in production.
_conversations: dict[str, list[ModelMessage]] = {}
MAX_HISTORY_MESSAGES = 40


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    conversation_id = request.conversation_id or uuid4().hex
    history = _conversations.get(conversation_id, [])

    try:
        result = await run_task_agent(request.message, AgentDeps(db=db), history)
    except ModelHTTPError as exc:  # LLM provider answered with an error (401 bad key, 429 rate limit, ...)
        logger.error(f"LLM HTTP error {exc.status_code}: {exc.body}")
        detail = "The LLM rejected the API key. Check LLM_API_KEY in backend/.env." if exc.status_code == 401 else f"The LLM provider returned an error ({exc.status_code})."
        raise HTTPException(status_code=502, detail=detail)
    except ModelAPIError as exc:  # could not reach the LLM at all
        logger.error(f"LLM connection error: {exc}")
        raise HTTPException(status_code=502, detail="Could not reach the LLM. Check LLM_BASE_URL and your network.")
    except (UnexpectedModelBehavior, UsageLimitExceeded) as exc:  # e.g. tool retries exhausted
        logger.error(f"Agent failed: {exc}")
        raise HTTPException(status_code=500, detail="The agent could not complete that request. Try rephrasing it.")
    except DatabaseError as exc:
        logger.error(f"Database error: {exc}")
        raise HTTPException(status_code=503, detail="The database is unavailable right now.")

    _conversations[conversation_id] = result.messages[-MAX_HISTORY_MESSAGES:]
    return ChatResponse(reply=result.reply, conversation_id=conversation_id, tool_calls=result.tool_calls)
