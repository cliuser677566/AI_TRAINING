# DRNKOO Backend

Run and test the FastAPI backend used by the DRNKOO project.

Install dependencies (recommended in a virtual environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Run the server:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

Quick test (after installing requirements):

```powershell
pytest -q
```

Notes:
- Default non-production login: `admin` / `password` (change before production).
- The service expects the SQLite DB at `database\drinkoo.db` created during Phase 1.

Chatbot setup:
- Copy env template and set OpenRouter values:

```powershell
Copy-Item backend\.env.example backend\.env
```

- Set environment variables before starting backend (PowerShell example):

```powershell
$env:OPENROUTER_API_KEY="<your-key>"
$env:OPENROUTER_MODEL="google/gemma-4-31b-it:free"
```

- Chat endpoint:
	- `POST /chatbot/message`
	- Request body: `{ "message": "...", "session_id": "optional" }`

Guardrails in chatbot:
- Max 4 user messages per session to control API cost.
- Answers only DRINKOO SKU/flavor/order topics.
- Blocks prompt-injection style requests and DB-modification intents.

Optional admin SQL debug mode (disabled by default):
- Set env vars:
	- `CHATBOT_SQL_DEBUG_ENABLED=1`
	- `CHATBOT_SQL_DEBUG_TOKEN=<strong-random-token>`
- Call `/chatbot/message` with:
	- body: `{ "message": "...", "debug_sql": true }`
	- header: `X-Chatbot-Debug-Token: <same-token>`
- Without both env + token, SQL debug metadata is not returned.

Examples:

- Ingest sales (POST /sales/ingest):

```powershell
curl -X POST http://localhost:8000/sales/ingest -H "Content-Type: application/json" -d '{"sales":[{"sku_id":1,"state_id":1,"quantity":10,"price":20.0}]}'
```

- Create a shipment (POST /shipments/):

```powershell
curl -X POST http://localhost:8000/shipments -H "Content-Type: application/json" -d '{"sku_id":1,"quantity":100,"from_state_id":1,"to_state_id":2}'
```

- Analytics: sales by state

```powershell
curl http://localhost:8000/analytics/sales_by_state
```

