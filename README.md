# Enterprise Knowledge Copilot

Enterprise Knowledge Copilot is a fullstack AI take-home project for an internal HR-policy chatbot. It uses a React + TypeScript chat UI, a FastAPI AI Gateway, a separate remote MCP Knowledge Server over Streamable HTTP, Groq's free OpenAI-compatible LLM API, Chroma semantic retrieval, synthetic HR policy documents, citations, feedback, and responsible-AI documentation.

## Architecture

```text
React Chat UI
  -> FastAPI AI Gateway via POST streaming
    -> Groq Free LLM via OpenAI-compatible API
       - decides whether to call tools
    -> FastAPI executes requested MCP tool calls
    -> Remote MCP Knowledge Server over Streamable HTTP
    -> Chroma + synthetic HR policy docs
    -> FastAPI sends tool results back to Groq
    -> Groq generates final grounded answer
  -> React displays streamed answer, citations, feedback
```

FastAPI is the only MCP host/client. Groq does not connect directly to the MCP server; it only emits OpenAI-compatible tool calls that FastAPI executes.

## Quick Start

See [RUNBOOK.md](RUNBOOK.md) for the full installation guide and exact commands.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt

cd frontend
npm install
cd ..

cp .env.example .env
# Edit OPENAI_API_KEY with a Groq Free Plan API key.

PYTHONPATH=mcp-server python mcp-server/scripts/ingest_documents.py
PYTHONPATH=mcp-server uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

In a second terminal:

```bash
source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In a third terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

## Demo Questions

- "Summarize our leave policy."
- "What is the escalation process for incidents?"
- "Find information about onboarding steps."
- "What is our policy for something not in the documents?"

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Design Rationale](docs/DESIGN.md)
- [Prompt and Tools](docs/PROMPT_AND_TOOLS.md)
- [Responsible AI](docs/RESPONSIBLE_AI.md)
- [Assumptions and Limitations](docs/ASSUMPTIONS_AND_LIMITATIONS.md)
- [Scale Out](docs/SCALE_OUT.md)
- [Deliverables Mapping](docs/DELIVERABLES_MAPPING.md)

