// Shows "what the agent did" under an assistant reply:
//   🔧 tool name → 📦 arguments → ✅/❌ result
import { useState } from "react";
import type { ToolCall } from "../types/chat";

function summarize(call: ToolCall): string {
  if (call.status === "error") return String(call.result);
  const r = call.result as Record<string, unknown> | unknown[] | null;
  if (Array.isArray(r)) return `${r.length} task${r.length === 1 ? "" : "s"} returned`;
  if (r && typeof r === "object") {
    if ("deleted" in r) return `Task ${r.task_id} deleted`;
    if ("id" in r) return `Task ${r.id} · ${r.title} · ${r.status}`;
  }
  return "Done";
}

export default function ToolCallTrace({ calls }: { calls: ToolCall[] }) {
  const [open, setOpen] = useState(true);
  if (calls.length === 0) return null;

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="text-sm text-muted hover:text-ink"
        aria-expanded={open}
      >
        {open ? "Hide" : "Show"} what the agent did ({calls.length} tool call{calls.length === 1 ? "" : "s"})
      </button>

      {open && (
        <ol className="mt-2 border-l-2 border-tool/40 pl-4 space-y-3">
          {calls.map((call, i) => {
            const failed = call.status === "error";
            return (
              <li key={i} className="relative">
                {/* dot on the rail */}
                <span
                  className={`absolute -left-[23px] top-1.5 h-3 w-3 rounded-full border-2 border-surface ${failed ? "bg-danger" : "bg-tool"}`}
                  aria-hidden
                />
                <div className={`rounded-md px-3 py-2 text-sm ${failed ? "bg-danger-tint" : "bg-tool-tint"}`}>
                  <p className="font-medium">
                    🔧 <span className="font-mono">{call.tool_name}</span>
                  </p>
                  <p className="mt-1 text-muted">
                    📦 <code className="font-mono text-[13px] text-ink break-all">{JSON.stringify(call.args)}</code>
                  </p>
                  <p className={`mt-1 ${failed ? "text-danger" : "text-tool"}`}>
                    {failed ? "❌" : "✅"} {summarize(call)}
                  </p>
                  <details className="mt-1">
                    <summary className="cursor-pointer text-xs text-muted">Raw result sent back to the LLM</summary>
                    <pre className="mt-1 overflow-x-auto rounded bg-surface p-2 font-mono text-xs">
                      {typeof call.result === "string" ? call.result : JSON.stringify(call.result, null, 2)}
                    </pre>
                  </details>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
