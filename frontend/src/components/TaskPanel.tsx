// Read-only view of the real database (GET /tasks). It refreshes after every agent reply,
// so you can SEE the agent's tool calls change the data.
import type { Task } from "../types/chat";

interface Props {
  tasks: Task[];
  error: string | null;
}

export default function TaskPanel({ tasks, error }: Props) {
  const pending = tasks.filter((t) => t.status === "pending").length;

  return (
    <aside className="hidden w-80 shrink-0 flex-col border-l border-line bg-surface lg:flex">
      <div className="border-b border-line px-5 py-4">
        <h2 className="font-semibold">Tasks in the database</h2>
        <p className="mt-0.5 text-sm text-muted">
          Read-only, from <code className="font-mono text-xs">GET /tasks</code>. Change them by chatting.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">
        {error ? (
          <p className="text-sm text-danger">{error}</p>
        ) : tasks.length === 0 ? (
          <p className="text-sm text-muted">No tasks yet. Ask the agent to create one.</p>
        ) : (
          <>
            <p className="mb-3 text-sm text-muted">
              {pending} pending, {tasks.length - pending} completed
            </p>
            <ul className="space-y-2">
              {tasks.map((task) => (
                <li key={task.id} className="flex items-start gap-3 rounded-md border border-line px-3 py-2">
                  <span className="font-mono text-xs text-muted pt-0.5">#{task.id}</span>
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm ${task.status === "completed" ? "text-muted line-through" : ""}`}>
                      {task.title}
                    </p>
                    {task.description && <p className="mt-0.5 text-xs text-muted">{task.description}</p>}
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 text-xs ${
                      task.status === "completed" ? "bg-tool-tint text-tool" : "bg-canvas text-muted"
                    }`}
                  >
                    {task.status}
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </aside>
  );
}
