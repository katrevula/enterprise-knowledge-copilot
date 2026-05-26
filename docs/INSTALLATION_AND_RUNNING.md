# Installation And Running Guide

This guide is for a reviewer or teammate starting from a clean machine. For the shorter operational checklist, see [../RUNBOOK.md](../RUNBOOK.md).

## Prerequisites

Install:

- Git
- Python 3.11 or newer
- Node.js 20 or newer
- npm 10 or newer
- A Groq API key, or another OpenAI-compatible provider key

Verify:

```bash
git --version
python3 --version
node --version
npm --version
```

On Windows, use `python --version` if `python3` is not available.

## 1. Get The Code

```bash
git clone <repository-url>
cd enterprise-knowledge-copilot
```

If the folder already exists, open a terminal at the repository root.

## 2. Configure Environment

Create `.env`:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=<your_api_key>
LLM_MODEL=llama-3.1-8b-instant
LLM_TIMEOUT_SECONDS=30
MIN_RELEVANCE_SCORE=0.45
MCP_SERVER_URL=http://localhost:8001/mcp
BACKEND_DATABASE_URL=storage/copilot.db
CHROMA_PERSIST_DIR=storage/chroma
HR_POLICY_DATA_DIR=data/hr_policies
HF_HOME=storage/huggingface
VITE_API_BASE_URL=http://localhost:8000
```

Optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed frontend origins for the gateway. |
| `CHROMA_COLLECTION_NAME` | `hr_policy_chunks` | Chroma collection name. |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model used by Chroma. |
| `MCP_FEEDBACK_DB` | `storage/mcp_feedback.db` | SQLite database for MCP feedback tool storage. |

Do not commit `.env`.

## 3. Install Python Dependencies

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt -r mcp-server/requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r backend\requirements.txt -r mcp-server\requirements.txt
```

Setup shortcuts are also available:

```bash
./scripts/setup-mac.sh
```

```powershell
.\scripts\setup-windows.ps1
```

If PowerShell blocks script execution for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup-windows.ps1
```

## 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

If a corporate npm proxy interferes on macOS, use:

```bash
cd frontend
npm install --cache /private/tmp/npm-cache --proxy=false --https-proxy=false --noproxy='*'
cd ..
```

## 5. Build The Knowledge Index

macOS/Linux:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "mcp-server"
.\.venv\Scripts\python.exe mcp-server\scripts\ingest_documents.py
```

Expected output includes:

```text
Knowledge index rebuilt
collection: hr_policy_chunks
document_count: 8
```

The first run may download the embedding model into `storage/huggingface/`.

## 6. Start The Services

Open three terminals from the repository root.

### Terminal 1: MCP Knowledge Server

macOS/Linux:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "mcp-server"
.\.venv\Scripts\uvicorn.exe mcp_server.main:app --host 0.0.0.0 --port 8001
```

### Terminal 2: FastAPI Gateway

macOS/Linux:

```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: React UI

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## 7. Validate The Running App

MCP server:

```bash
curl http://localhost:8001/health
```

FastAPI gateway:

```bash
curl http://localhost:8000/api/health
```

Frontend:

```bash
curl -I http://localhost:5173/
```

Try these prompts in the UI:

- "Summarize our leave policy."
- "What is the escalation process for incidents?"
- "Find information about onboarding steps."
- "What is our policy for something not in the documents?"

The first three should produce source-backed answers. The last should exercise insufficient-evidence behavior when no relevant source is found.

## 8. Run Tests And Build

Backend:

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests
```

MCP server:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server pytest mcp-server/tests
```

Frontend tests:

```bash
cd frontend
npm test
```

Frontend production build:

```bash
cd frontend
npm run build
```

Python compile check:

```bash
.venv/bin/python -m compileall -q backend mcp-server
```

## 9. Stop Services

Press `Ctrl+C` in each service terminal.

Generated local data is under `storage/`. Removing `storage/` clears runtime databases and the Chroma index; re-run ingestion before the next demo.

## 10. Common Issues

| Issue | Resolution |
| --- | --- |
| `OPENAI_API_KEY is not configured` | Add the key to `.env` and restart the FastAPI gateway. |
| Backend health shows `"llm_configured": false` | The gateway process did not read a valid key. Confirm `.env` and restart. |
| `Connection refused` for MCP | Start the MCP server and verify `MCP_SERVER_URL=http://localhost:8001/mcp`. |
| Empty retrieval results | Re-run the ingestion script and confirm `storage/chroma/` exists. |
| Weak or missing citations | Check `MIN_RELEVANCE_SCORE`; lower only if valid policy questions are being filtered out. |
| Frontend API failures | Confirm backend health and `VITE_API_BASE_URL`. |
| Port conflict | Stop the existing process or update ports and dependent configuration. |
| Hosted LLM rate limit | Wait for quota reset or configure another OpenAI-compatible provider. |
