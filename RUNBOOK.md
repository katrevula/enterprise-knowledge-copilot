# Runbook

This runbook describes the standard local operating procedure for Enterprise Knowledge Copilot. It is optimized for repeatable evaluator setup, smoke testing, and troubleshooting.

## Runtime Topology

| Service | Port | Command Owner | Purpose |
| --- | ---: | --- | --- |
| React UI | `5173` | `frontend/` | Chat interface and feedback controls. |
| FastAPI Gateway | `8000` | `backend/` | Chat API, streaming, LLM calls, MCP client, persistence. |
| MCP Knowledge Server | `8001` | `mcp-server/` | Policy search tools, Chroma retrieval, MCP feedback tool. |

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm 10 or newer
- A Groq API key, or another OpenAI-compatible provider configured through `.env`

Verify local versions:

```bash
python3 --version
node --version
npm --version
```

## Environment Configuration

Create local configuration:

```bash
cp .env.example .env
```

Required values:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes | none | API key for the configured OpenAI-compatible LLM provider. |
| `OPENAI_BASE_URL` | Yes | `https://api.groq.com/openai/v1` | LLM API base URL. |
| `LLM_MODEL` | Yes | `llama-3.1-8b-instant` | Model used for tool planning and final answer generation. |
| `MCP_SERVER_URL` | Yes | `http://localhost:8001/mcp` | Remote MCP endpoint used by the FastAPI gateway. |
| `BACKEND_DATABASE_URL` | No | `storage/copilot.db` | SQLite database for conversations, citations, feedback, and audits. |
| `CHROMA_PERSIST_DIR` | No | `storage/chroma` | Local Chroma index directory. |
| `HR_POLICY_DATA_DIR` | No | `data/hr_policies` | Markdown policy corpus directory. |
| `MIN_RELEVANCE_SCORE` | No | `0.45` | Minimum retrieval score required for a citation to be treated as grounded. |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Frontend API base URL. |

Do not commit `.env`.

## First-Time Setup

macOS shortcut:

```bash
./scripts/setup-mac.sh
```

Manual setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt -r mcp-server/requirements.txt

cd frontend
npm install
cd ..
```

Build the local retrieval index:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py
```

The ingestion step reads `data/hr_policies/*.md`, chunks the documents, generates embeddings, and writes the Chroma index to `storage/chroma/`.

## Start Services

Terminal 1, MCP Knowledge Server:

```bash
source .venv/bin/activate
PYTHONPATH=mcp-server uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

Terminal 2, FastAPI Gateway:

```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 3, React UI:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Health Checks

MCP server:

```bash
curl http://localhost:8001/health
```

Expected shape:

```json
{"status":"ok","service":"remote-mcp-knowledge-server","transport":"streamable-http","mcp_path":"/mcp"}
```

FastAPI gateway:

```bash
curl http://localhost:8000/api/health
```

Expected shape:

```json
{"status":"ok","service":"fastapi-ai-gateway","llm_configured":true}
```

Frontend:

```bash
curl -I http://localhost:5173/
```

Expected result: HTTP `200 OK`.

## Quality Gates

Run these before packaging or handoff:

```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests
PYTHONPATH=mcp-server pytest mcp-server/tests
.venv/bin/python -m compileall -q backend mcp-server
```

```bash
cd frontend
npm test
npm run build
```

## Operational Notes

- The first ingestion or server start can download the embedding model into `storage/huggingface/`.
- Runtime data is local and ignored by Git under `storage/`.
- Feedback is written by the gateway and also sent to the MCP feedback tool when available.
- `MIN_RELEVANCE_SCORE` protects unsupported questions from receiving unrelated citations.
- If the MCP server is unavailable, tool listing falls back to local schemas, but actual tool execution still requires the MCP server.

## Troubleshooting

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| `OPENAI_API_KEY is not configured` | Missing key in `.env` or gateway not restarted. | Set `OPENAI_API_KEY`, then restart FastAPI. |
| Backend health has `"llm_configured": false` | API key missing. | Update `.env`; do not rely on shell-only exports unless the process uses them. |
| MCP connection error | MCP server not running or wrong URL. | Check `curl http://localhost:8001/health` and `MCP_SERVER_URL`. |
| Empty or weak citations | Index missing or stale. | Rerun `PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py`. |
| Frontend cannot reach backend | Wrong `VITE_API_BASE_URL` or backend is stopped. | Start backend on `8000` or set `VITE_API_BASE_URL`. |
| Port already in use | Previous service instance still running. | Stop the existing process or use a different port and update dependent config. |
| Groq rate-limit error | Free provider quota exceeded. | Wait for reset or configure another OpenAI-compatible provider. |

## Shutdown

Press `Ctrl+C` in each terminal running a service. Generated local data can be removed by deleting `storage/`, but doing so requires re-running ingestion before the next demo.
