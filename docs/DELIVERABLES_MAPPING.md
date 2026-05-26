# Deliverables Mapping

This file maps expected project deliverables to concrete implementation locations.

## Implementation Deliverables

| Requirement | Location | Notes |
| --- | --- | --- |
| Frontend application | `frontend/` | React + TypeScript chat UI with streaming response rendering. |
| Backend application | `backend/` | FastAPI gateway, LLM orchestration, SSE streaming, persistence. |
| Remote MCP server | `mcp-server/` | Streamable HTTP MCP tools for retrieval and feedback. |
| Dataset | `data/hr_policies/` | Eight synthetic HR policy Markdown documents. |
| Retrieval/indexing | `mcp-server/scripts/ingest_documents.py`, `mcp-server/mcp_server/knowledge_base.py` | Chroma index rebuild and search implementation. |
| Prompt and tool design | `docs/PROMPT_AND_TOOLS.md`, `backend/app/agent.py` | System prompt, tool loop, streaming event contract. |
| AI interaction improvements | `frontend/src/App.tsx`, `backend/app/agent.py` | Activity states, citations, feedback, insufficient-evidence handling. |
| Persistence | `backend/app/database.py`, `mcp-server/mcp_server/feedback_store.py` | Local SQLite storage for conversations, feedback, and audit metadata. |

## Documentation Deliverables

| Requirement | Location |
| --- | --- |
| Project overview and quick start | `README.md` |
| Operational runbook | `RUNBOOK.md` |
| Detailed installation guide | `docs/INSTALLATION_AND_RUNNING.md` |
| Architecture narrative | `docs/ARCHITECTURE.md` |
| Architecture diagrams | `docs/DIAGRAMS.md` |
| Design rationale | `docs/DESIGN.md` |
| Responsible AI and governance | `docs/RESPONSIBLE_AI.md` |
| Assumptions and limitations | `docs/ASSUMPTIONS_AND_LIMITATIONS.md` |
| Scale-out plan | `docs/SCALE_OUT.md` |

## Constraint Coverage

| Constraint | Coverage |
| --- | --- |
| Runnable on standard developer hardware | Local Python, Node, Chroma, and SQLite setup documented in `RUNBOOK.md`. |
| No paid infrastructure required | Default provider uses a free OpenAI-compatible hosted LLM option; all storage is local. |
| Synthetic/public-safe data | The corpus is synthetic Markdown under `data/hr_policies/`. |
| Source-grounded behavior | MCP retrieval, citations, relevance filtering, and insufficient-evidence handling. |
| Reviewable operational process | Health checks, tests, build commands, and troubleshooting documented. |
| Production limitations documented | Governance, scale-out, and limitations docs state gaps and next steps. |
