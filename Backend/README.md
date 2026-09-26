# Backend — FastAPI + PydanticAI + SQLite

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # set LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
python demo_offline.py          # full flow with a fake LLM, no key needed
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

Layers (each only calls the one below): `api/` → `agents/` → `tools/` → `services/` → `models/` + `database/`.
`schemas/` holds the Pydantic models shared by the API and the tools.

See the top-level README.md for the full walkthrough and file-by-file explanation.
