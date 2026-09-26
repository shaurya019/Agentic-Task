"""
logger.py — Tiny logging helper that prints each layer of the agent flow.

Every layer calls `log_step("LAYER", "message")`, so in your terminal you see:

    USER:      "Delete my task called Learn LangGraph"
    AGENT:     LLM chose tool -> delete_task
    TOOL:      delete_task(task_id=3)
    DATABASE:  Task 3 deleted
    AGENT:     "Done, I deleted the task."
"""
import logging

from app.config import settings

logging.basicConfig(level=settings.log_level, format="%(message)s")
logger = logging.getLogger("agentic_tasks")

# Keep third-party libraries quiet so our flow logs are easy to read.
for noisy in ("httpx", "httpcore", "openai"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def log_step(layer: str, message: str) -> None:
    """Print one step of the flow, e.g. log_step("TOOL", "delete_task(task_id=3)")."""
    logger.info(f"{layer + ':':<10} {message}")
