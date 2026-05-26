# RUNBOOK: Install, Configure, Run

This runbook is the reproducible setup guide for the Enterprise Knowledge Copilot.

For more detailed macOS and Windows instructions, see [Detailed Installation And Running Guide](docs/INSTALLATION_AND_RUNNING.md).

## 1. Required Installations

Install these public/free tools:

- Python 3.11+
- Node.js 20+
- npm 10+
- A Groq Free Plan API key from `https://console.groq.com/keys`

Check local versions:

```bash
python3 --version
node --version
npm --version
```

## 2. Python Environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt
```

macOS shortcut:

```bash
./scripts/setup-mac.sh
```

Windows PowerShell shortcut:

```powershell
.\scripts\setup-windows.ps1
```

## 3. Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## 4. Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=<your_groq_api_key>
LLM_MODEL=llama-3.1-8b-instant
LLM_TIMEOUT_SECONDS=30
MCP_SERVER_URL=http://localhost:8001/mcp
BACKEND_DATABASE_URL=storage/copilot.db
CHROMA_PERSIST_DIR=storage/chroma
HR_POLICY_DATA_DIR=data/hr_policies
HF_HOME=storage/huggingface
```

## 5. Build the HR Knowledge Index

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py
```

This reads synthetic HR Markdown documents from `data/hr_policies/` and writes a local Chroma index under `storage/chroma/`.

## 6. Run the Remote MCP Server

Terminal 1:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

Health check:

```bash
curl http://localhost:8001/health
```

MCP endpoint:

```text
http://localhost:8001/mcp
```

## 7. Run the FastAPI AI Gateway

Terminal 2:

```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## 8. Run the React Frontend

Terminal 3:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## 9. Run Tests

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

Frontend:

```bash
cd frontend
npm test
```

## 10. Troubleshooting

- Missing Groq key: confirm `OPENAI_API_KEY` is set in `.env`.
- Groq rate limit: wait for quota reset or use a different free-compatible model/provider.
- MCP connection error: confirm the MCP server is running on port `8001` and `MCP_SERVER_URL` ends with `/mcp`.
- Empty search results: rerun `PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py`.
- Port conflict: run the affected service on another port and update `.env` or `VITE_API_BASE_URL`.
- First ingestion is slow: the public embedding model may download on first run.
