# Architecture

Enterprise Knowledge Copilot is split into three runtime services: a browser UI, an AI gateway, and a remote MCP knowledge server. The design keeps user experience, model orchestration, and retrieval tooling separate so each layer can be tested, scaled, or replaced independently.

## Goals

- Provide a usable local HR policy assistant with streamed responses.
- Ground answers in retrieved source excerpts rather than free-form model memory.
- Demonstrate a remote MCP server boundary instead of embedding retrieval directly in the UI or gateway.
- Keep runtime dependencies local except for the configured OpenAI-compatible LLM provider.
- Preserve a clear path from proof of concept to production hardening.

## Component Responsibilities

| Component | Technology | Responsibilities | Does Not Own |
| --- | --- | --- | --- |
| React UI | React, TypeScript, Vite | Chat layout, prompt entry, streamed event rendering, citations, feedback buttons. | LLM calls, retrieval, secrets, persistence. |
| FastAPI Gateway | FastAPI, OpenAI SDK, MCP client, SQLite | Chat API, conversation state, SSE formatting, LLM tool loop, MCP calls, audit events. | Vector indexing, source document parsing, browser rendering. |
| MCP Knowledge Server | FastMCP, Starlette, Chroma | Tool schemas, semantic search, exact excerpt lookup, policy resource listing, MCP feedback capture. | User sessions, LLM provider calls, frontend state. |
| Retrieval Store | Chroma, sentence-transformers | Embeddings, vector search, source metadata. | Business orchestration or authorization. |
| Runtime Store | SQLite | Conversations, messages, citations, feedback, audit events. | Long-term production compliance storage. |

## Request Lifecycle

1. The user submits a policy question in the React UI.
2. The UI opens a POST streaming request to `POST /api/chat/stream`.
3. FastAPI stores the user message and builds the model context from recent conversation history.
4. FastAPI lists MCP tools and sends OpenAI-compatible tool schemas to the LLM.
5. The LLM may request an MCP tool call, such as `search_hr_knowledge_base`.
6. FastAPI executes the tool call against the remote MCP server at `MCP_SERVER_URL`.
7. Search results below `MIN_RELEVANCE_SCORE` are filtered before final answer generation.
8. FastAPI sends the retained tool results back to the LLM as grounded context.
9. The final answer is streamed to the UI as SSE-style events over the fetch response.
10. Citations, status, latency, and completion metadata are stored and rendered.

## Public Interfaces

### FastAPI Gateway

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/health` | `GET` | Health and model configuration status. |
| `/api/chat/stream` | `POST` | Streams chat status, tool activity, tokens, citations, and completion metadata. |
| `/api/conversations/{conversation_id}` | `GET` | Returns stored messages and citations for a conversation. |
| `/api/feedback` | `POST` | Stores answer feedback and forwards it to the MCP feedback tool when possible. |

### MCP Knowledge Server

| Interface | Purpose |
| --- | --- |
| `/health` | HTTP health check. |
| `/mcp` | Streamable HTTP MCP endpoint. |
| `search_hr_knowledge_base(query, top_k)` | Semantic policy search. |
| `get_policy_excerpt(source_id, chunk_id)` | Exact excerpt retrieval. |
| `list_policy_resources()` | Lists available synthetic policy resources. |
| `record_feedback(message_id, rating, comment?)` | Records answer feedback through MCP. |

## Streaming Events

The chat stream uses SSE-formatted event blocks over a POST `fetch()` stream. Event names currently emitted by the gateway are:

| Event | Purpose |
| --- | --- |
| `status` | Lifecycle state such as request received, planning, or generating. |
| `tool_call` | Tool name and safe argument metadata for the UI activity panel. |
| `token` | Incremental answer text. |
| `citations` | Source excerpts retained after relevance filtering. |
| `done` | Final answer payload and grounded/insufficient-evidence status. |
| `complete` | Stored assistant message ID, conversation ID, and latency. |
| `error` | User-visible failure message and optional hint. |

## Persistence

| Store | Path | Contents |
| --- | --- | --- |
| SQLite gateway database | `storage/copilot.db` | Conversations, messages, citations, feedback, audit events. |
| Chroma index | `storage/chroma/` | Embedded document chunks and metadata. |
| MCP feedback database | `storage/mcp_feedback.db` | Feedback received through the MCP tool. |
| Hugging Face cache | `storage/huggingface/` | Downloaded embedding model files. |

All generated runtime storage is ignored by Git.

## Deployment Boundary

The current deployment is local development only. In a production deployment, the UI, gateway, MCP server, vector store, relational database, and observability stack should be deployed and secured independently. The existing service split is intentionally compatible with that future shape.

For visual diagrams, see [DIAGRAMS.md](DIAGRAMS.md).
