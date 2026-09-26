"""
main.py — Creates the FastAPI app, wires up CORS, routers and the database.

Run with:  uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, tasks
from app.config import settings
from app.database.database import init_db
from app.logger import logger


@asynccontextmanager
# asynccontextmanager comes from Python's contextlib. It turns an async generator function into an async context manager, which is something you can use with async with. In your app, FastAPI uses it to run code when the server starts and when it shuts down.
async def lifespan(app: FastAPI):
    init_db()  # create the tasks table on startup
    logger.info(f"Model: {settings.llm_model} @ {settings.llm_base_url}")
    if not settings.llm_api_key and "api.openai.com" in settings.llm_base_url:
        logger.warning("LLM_API_KEY is empty: /chat will fail until you set it in backend/.env")
    yield
    

app = FastAPI(title="Agentic Task Manager", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(tasks.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "model": settings.llm_model}

    