// The message box. Enter sends, Shift+Enter adds a new line.
import { useState, type KeyboardEvent } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  function send() {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="flex items-end gap-2 rounded-xl border border-line bg-surface p-2 shadow-sm focus-within:border-user">
      <label htmlFor="chat-input" className="sr-only">Message the task agent</label>
      <textarea
        id="chat-input"
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder='Try "Create a task called Learn Agentic AI"'
        maxLength={2000}
        className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1.5 outline-none placeholder:text-muted"
      />
      <button
        type="button"
        onClick={send}
        disabled={disabled || !text.trim()}
        className="rounded-lg bg-user px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
      >
        Send
      </button>
    </div>
  );
}
