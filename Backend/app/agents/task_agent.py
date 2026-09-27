"""
agents/task_agent.py — The agent: an LLM + a system prompt + a set of tools.

How one agent run works (PydanticAI does this loop for you):

    1. Send to the LLM: system prompt + chat history + user message + tool schemas
    2. LLM replies EITHER with plain text (done) OR with "please call tool X with args Y"
    3. PydanticAI validates args Y, runs tool X, and sends the result back to the LLM
    4. Go back to step 2 until the LLM answers with plain text

Everything the LLM "decides" happens in step 2. Everything that touches data happens
in step 3, inside our own code.
"""
from dataclasses import dataclass
from datetime import date

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, RetryPromptPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_core import to_jsonable_python

from app.config import settings
from app.logger import log_step
from app.schemas.chat import ToolCallInfo
from app.tools.task_tools import TASK_TOOLS, AgentDeps

# ---------------------------------------------------------------------------
# 1. The model: any OpenAI-compatible endpoint (OpenAI, Groq, OpenRouter, Ollama...)
# ---------------------------------------------------------------------------
model = OpenAIChatModel(
    settings.llm_model,
    provider=OpenAIProvider(
        base_url=settings.llm_base_url,
        # Local servers like Ollama ignore the key, but the client needs a non-empty string.
        api_key=settings.llm_api_key or "not-set",
    ),
)

# ---------------------------------------------------------------------------
# 2. The system prompt: the agent's job description and rules.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a helpful task-management assistant. You manage the user's tasks ONLY by
calling the provided tools. Never invent tasks, ids or results.

Rules:
- To act on a task the user names by title (e.g. "the LangGraph task"), first call
  list_tasks with title_contains to find its id, then call the right tool with that id.
- If several tasks match, ask the user which one they mean instead of guessing.
- "Done", "finished" or "complete" means update_task with status='completed'.
- If a tool returns an error, explain it simply; do not pretend it succeeded.
- Keep replies short and friendly. When listing tasks, show id, title and status.
"""

# ---------------------------------------------------------------------------
# 3. The agent: model + prompt + tools (+ the type of dependencies tools receive)
# ---------------------------------------------------------------------------
task_agent = Agent(
    model,
    deps_type=AgentDeps,
    instructions=SYSTEM_PROMPT,
    tools=TASK_TOOLS,  # <- tool registration: each function becomes a tool the LLM can call
    retries=3,  # how many times a tool may ask the LLM to fix bad arguments
)


@task_agent.instructions
def add_today(ctx: RunContext[AgentDeps]) -> str:
    """Dynamic instructions are added on every run — handy for context like the date."""
    return f"Today's date is {date.today().isoformat()}."


# ---------------------------------------------------------------------------
# 4. Running the agent loop step by step and recording what it did
# ---------------------------------------------------------------------------
@dataclass
class AgentRunResult:
    reply: str
    tool_calls: list[ToolCallInfo]
    messages: list[ModelMessage]  # full history, saved so the next turn has context


def short_error(part: RetryPromptPart) -> str:
    """Turn a retry prompt into one readable line, e.g. 'task_id: Input should be greater than 0'."""
    if isinstance(part.content, str):
        return part.content
    return "; ".join(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in part.content)


def _collect_tool_calls(messages: list[ModelMessage]) -> list[ToolCallInfo]:
    """Pair every tool call the LLM made with the result our tool sent back.

    The message history of one run looks like:
        ModelRequest   [UserPromptPart]                 <- user message
        ModelResponse  [ToolCallPart(list_tasks, ...)]  <- LLM asks for a tool
        ModelRequest   [ToolReturnPart(...)]            <- our tool's result
        ModelResponse  [ToolCallPart(delete_task, ...)] <- LLM asks for another
        ModelRequest   [ToolReturnPart(...)]
        ModelResponse  [TextPart("Done ...")]           <- final answer
    """
    calls: dict[str, ToolCallPart] = {}
    trace: list[ToolCallInfo] = []
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                calls[part.tool_call_id] = part
            elif isinstance(part, (ToolReturnPart, RetryPromptPart)) and part.tool_name:
                call = calls.get(part.tool_call_id)
                args = call.args_as_dict() if call else {}
                if isinstance(part, ToolReturnPart):
                    trace.append(ToolCallInfo(tool_name=part.tool_name, args=args, status="success",
                                              result=to_jsonable_python(part.content)))
                else:  # invalid arguments or ModelRetry raised by the tool
                    trace.append(ToolCallInfo(tool_name=part.tool_name, args=args, status="error",
                                              result=short_error(part)))
    return trace


async def run_task_agent(user_message: str, deps: AgentDeps, history: list[ModelMessage]) -> AgentRunResult:
    log_step("USER", repr(user_message))

    # agent.iter() lets us watch the loop one node at a time. (agent.run() does the
    # same thing in one call — we only iterate so we can log each decision.)
    async with task_agent.iter(user_message, deps=deps, message_history=history) as run:
        async for node in run:
            if Agent.is_call_tools_node(node):
                # The LLM just answered. Did it choose tools or write the final text?
                for part in node.model_response.parts:
                    if isinstance(part, ToolCallPart):
                        log_step("AGENT", f"LLM chose tool -> {part.tool_name} {part.args_as_dict()}")
            # Tools run when the loop advances past a CallToolsNode; their logs come from tools/ and services/.

    result = run.result
    assert result is not None
    new_messages = result.new_messages()
    for info in _collect_tool_calls(new_messages):
        if info.status == "error":
            log_step("AGENT", f"{info.tool_name} failed, LLM was asked to fix it: {info.result}")
    log_step("AGENT", repr(result.output))
    return AgentRunResult(reply=result.output, tool_calls=_collect_tool_calls(new_messages), messages=result.all_messages())
