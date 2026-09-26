// Page layout: header, chat on the left, live database view on the right.
import { useCallback, useEffect, useState } from "react";
import Chat from "./components/Chat";
import TaskPanel from "./components/TaskPanel";
import { fetchTasks } from "./services/api";
import type { Task } from "./types/chat";

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskError, setTaskError] = useState<string | null>(null);

  const refreshTasks = useCallback(async () => {
    try {
      setTasks(await fetchTasks());
      setTaskError(null);
    } catch (err) {
      setTaskError(err instanceof Error ? err.message : "Could not load tasks.");
    }
  }, []);

  useEffect(() => {
    refreshTasks();
  }, [refreshTasks]);

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b border-line bg-surface px-5 py-3">
        <h1 className="font-semibold">Task Agent</h1>
        <p className="text-sm text-muted">React → FastAPI → Agent → Tools → SQLite</p>
      </header>
      <main className="flex min-h-0 flex-1">
        <Chat onAgentReply={refreshTasks} />
        <TaskPanel tasks={tasks} error={taskError} />
      </main>
    </div>
  );
}
