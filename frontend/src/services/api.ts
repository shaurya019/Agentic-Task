// All HTTP calls live here, so components never deal with fetch() details.
import type { ChatRequest, ChatResponse, Task } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new Error(`Can't reach the backend at ${API_URL}. Is uvicorn running?`);
  }
  if (!res.ok) {
    // FastAPI puts error messages in { detail: ... }
    const body = await res.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : `Request failed (${res.status})`;
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

/** Writes go through the agent: the UI only sends natural language. */
export function sendChatMessage(body: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", { method: "POST", body: JSON.stringify(body) });
}

/** Reads can go straight to the REST API: used by the read-only task panel. */
export function fetchTasks(): Promise<Task[]> {
  return request<Task[]>("/tasks");
}
