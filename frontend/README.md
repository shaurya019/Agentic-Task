# Frontend — React + TypeScript + Tailwind (Vite)

```bash
npm install
npm run dev        # http://localhost:5173  (backend must run on :8000)
```

Set `VITE_API_URL` in `.env` (copy `.env.example`) if the backend runs elsewhere.

- `components/Chat.tsx` sends every message to `POST /chat` and keeps the `conversation_id`.
- `components/ToolCallTrace.tsx` shows the tools the agent called, with arguments and results.
- `components/TaskPanel.tsx` reads `GET /tasks` after each reply so you can watch the database change.

See the top-level README.md for the full walkthrough.
