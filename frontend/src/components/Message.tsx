// Renders one chat bubble: the user's message, the agent's reply (+ tool trace), or an error.
import type { ChatMessage } from "../types/chat";
import ToolCallTrace from "./ToolCallTrace";

export default function Message({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <p className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-user px-4 py-2.5 text-white">
          {message.content}
        </p>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div role="alert" className="rounded-lg border border-danger/30 bg-danger-tint px-4 py-3 text-sm text-danger">
        {message.content}
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <span className="mt-0.5 text-xl" aria-hidden>🤖</span>
      <div className="min-w-0 flex-1">
        {/* Tool calls happen BEFORE the final reply, so show them first. */}
        {message.toolCalls && <ToolCallTrace calls={message.toolCalls} />}
        <p className="mt-2 whitespace-pre-wrap leading-relaxed">{message.content}</p>
      </div>
    </div>
  );
}
