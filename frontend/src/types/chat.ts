// These types mirror the backend's Pydantic schemas (app/schemas/*.py).
// If you change a schema in Python, change it here too.

export type TaskStatus = "pending" | "completed";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

/** One tool call the agent made (backend: ToolCallInfo). */
export interface ToolCall {
  tool_name: string;
  args: Record<string, unknown>;
  status: "success" | "error";
  result: unknown;
}

/** Body of POST /chat (backend: ChatRequest). */
export interface ChatRequest {
  message: string;
  conversation_id: string | null;
}

/** Response of POST /chat (backend: ChatResponse). */
export interface ChatResponse {
  reply: string;
  conversation_id: string;
  tool_calls: ToolCall[];
}

/** A message as the UI stores it. */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
  toolCalls?: ToolCall[];
}
