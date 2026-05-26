# Detailed Installation And Running Guide

This guide is for a new evaluator or teammate running the project from a clean machine.

## Prerequisites

Install these first:

- Git
- Python 3.11 or newer
- Node.js 20 or newer
- npm 10 or newer
- A free Groq API key from `https://console.groq.com/keys`

Verify:

```bash
git --version
python3 --version
node --version
npm --version
```

On Windows, use:

```powershell
git --version
python --version
node --version
npm --version
```

## 1. Get The Code

```bash
git clone <repository-url>
cd enterprise-knowledge-copilot
```

If you already have the folder, open a terminal at the repository root.

## 2. Configure Environment Variables

Create `.env` from the example:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:

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
VITE_API_BASE_URL=http://localhost:8000
```

Do not commit `.env`.

## 3. macOS Setup

Recommended shortcut:

```bash
./scripts/setup-mac.sh
```

Manual macOS setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt -r mcp-server/requirements.txt

cd frontend
npm install --cache /private/tmp/npm-cache --proxy=false --https-proxy=false --noproxy='*'
cd ..

PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py
```

## 4. Windows Setup

Recommended shortcut:

```powershell
.\scripts\setup-windows.ps1
```

If PowerShell blocks script execution for this terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup-windows.ps1
```

Manual Windows setup:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r backend\requirements.txt -r mcp-server\requirements.txt

cd frontend
npm install
cd ..

$env:PYTHONPATH = "mcp-server"
.\.venv\Scripts\python.exe mcp-server\scripts\ingest_documents.py
```

## 5. Run The Project On macOS

Open three terminals from the repository root.

Terminal 1, MCP server:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

Terminal 2, FastAPI gateway:

```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 3, React frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## 6. Run The Project On Windows

Open three PowerShell terminals from the repository root.

Terminal 1, MCP server:

```powershell
$env:PYTHONPATH = "mcp-server"
.\.venv\Scripts\uvicorn.exe mcp_server.main:app --host 0.0.0.0 --port 8001
```

Terminal 2, FastAPI gateway:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 3, React frontend:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## 7. Health Checks

MCP server:

```bash
curl http://localhost:8001/health
```

FastAPI gateway:

```bash
curl http://localhost:8000/api/health
```

Expected backend result includes:

```json
"llm_configured": true
```

Frontend:

```text
http://localhost:5173
```

## 8. Demo Questions

Try:

- "Summarize our leave policy."
- "What is the escalation process for incidents?"
- "Find information about onboarding steps."
- "What is our policy for something not in the documents?"

## 9. Stop The Services

Press `Ctrl+C` in each terminal running a service.

## 10. Common Issues

- `OPENAI_API_KEY is not configured`: set the Groq key in `.env` and restart FastAPI.
- Groq `429` or rate-limit errors: wait for the free quota to reset or use another OpenAI-compatible free provider.
- MCP connection error: confirm `http://localhost:8001/health` returns `ok`.
- Empty answers or no citations: rerun document ingestion.
- Python cannot import app modules: make sure `PYTHONPATH` is set as shown above.
- npm proxy issue on macOS: use the macOS npm command with `--proxy=false --https-proxy=false --noproxy='*'`.

