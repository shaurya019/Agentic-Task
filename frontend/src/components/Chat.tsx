// The chat screen: owns the message list, the loading state and the conversation id.
//
// Flow for one message:
//   1. user types -> handleSend()
//   2. POST /chat { message, conversation_id }
//   3. backend agent runs tools, replies with { reply, tool_calls, conversation_id }
//   4. we append the reply (with its tool calls) and refresh the task panel
import { useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../services/api";
import type { ChatMessage } from "../types/chat";
import ChatInput from "./ChatInput";
import Message from "./Message";

const EXAMPLES = [
  'Create a task called "Learn LangGraph"',
  "Show me all my tasks",
  'Update the LangGraph task to "Learn LangGraph and tool calling"',
  "Mark the LangGraph task as done",
  "What tasks are currently pending?",
  "Delete the LangGraph task",
];

const newId = () => crypto.randomUUID();

export default function Chat({ onAgentReply }: { onAgentReply: () => void }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  // The backend uses this id to remember earlier turns of the conversation.
  const [conversationId, setConversationId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text: string) {
    setMessages((prev) => [...prev, { id: newId(), role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await sendChatMessage({ message: text, conversation_id: conversationId });
      setConversationId(res.conversation_id);
      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "assistant", content: res.reply, toolCalls: res.tool_calls },
      ]);
      onAgentReply(); // the agent may have changed data -> refresh the task panel
    } catch (err) {
      const content = err instanceof Error ? err.message : "Something went wrong.";
      setMessages((prev) => [...prev, { id: newId(), role: "error", content }]);
    } finally {
      setLoading(false);
    }
  }

  function startOver() {
    setMessages([]);
    setConversationId(null);
  }

  return (
    <section className="flex min-w-0 flex-1 flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-2xl space-y-6 px-4 py-8">
          {messages.length === 0 && (
            <div>
              <h2 className="text-2xl font-semibold">Manage tasks by chatting</h2>
              <p className="mt-2 max-w-prose text-muted">
                Each reply shows the tools the agent called, the arguments the LLM generated, and what the
                database returned. Pick an example to start:
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    onClick={() => handleSend(ex)}
                    className="rounded-full border border-line bg-surface px-3 py-1.5 text-sm hover:border-user hover:text-user"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <Message key={m.id} message={m} />
          ))}

          {loading && (
            <div className="flex items-center gap-3 text-muted" role="status">
              <span className="text-xl" aria-hidden>🤖</span>
              <span className="flex gap-1" aria-hidden>
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted [animation-delay:-0.3s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted [animation-delay:-0.15s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted" />
              </span>
              <span className="text-sm">Thinking and calling tools…</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t border-line bg-canvas px-4 py-4">
        <div className="mx-auto max-w-2xl">
          <ChatInput onSend={handleSend} disabled={loading} />
          <div className="mt-2 flex justify-between text-xs text-muted">
            <span>Enter to send, Shift+Enter for a new line</span>
            {messages.length > 0 && (
              <button type="button" onClick={startOver} className="hover:text-ink">
                Start a new conversation
              </button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
