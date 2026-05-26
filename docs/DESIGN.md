# Design Rationale

This document explains the main implementation choices and tradeoffs behind Enterprise Knowledge Copilot.

## Design Principles

- Keep the user experience responsive with streamed status and answer tokens.
- Put all sensitive configuration and model orchestration on the server side.
- Use MCP as a real service boundary, not just an in-process helper abstraction.
- Prefer source-grounded answers over broad model recall.
- Make the local proof of concept easy to run, inspect, and extend.

## Key Decisions

| Decision | Rationale | Tradeoff |
| --- | --- | --- |
| React + Vite frontend | Fast local development, TypeScript safety, simple streaming fetch support. | No server-side rendering or packaged desktop app. |
| FastAPI gateway | Strong async support, simple Pydantic contracts, familiar Python ecosystem for LLM and MCP clients. | Requires a separate Python service alongside the UI. |
| Gateway-owned tool loop | The hosted LLM cannot reach local MCP services directly; FastAPI can safely execute tool calls and control persistence. | More orchestration code in the backend. |
| Remote MCP knowledge server | Models an enterprise tool boundary that could later sit behind authorization, logging, or independent scaling. | Adds a third local process for the POC. |
| Chroma local vector store | Demonstrates semantic retrieval and source metadata without a managed vector database. | Not a production search platform by itself. |
| SQLite local persistence | Simple durable storage for conversation and feedback history. | Not intended for multi-node production traffic. |
| Synthetic HR corpus | Keeps the project reviewable and safe while matching the assistant use case. | Smaller and cleaner than a real policy corpus. |

## Grounding Strategy

The assistant is instructed to answer from MCP-retrieved content. Retrieval is performed by the MCP server and returned with source metadata. The gateway applies `MIN_RELEVANCE_SCORE` before treating results as citations. If no citations survive filtering, the final prompt includes an explicit instruction to state that the current knowledge base lacks enough information.

This design does not guarantee perfect factuality, but it reduces unsupported answers and gives reviewers a clear source trail.

## User Experience Decisions

- The activity panel exposes request lifecycle states and MCP tool calls so the user can see the system doing retrieval work.
- Citations are shown below answers rather than hidden in logs.
- Feedback is intentionally lightweight: helpful or needs work. The POC stores enough information to support later review without creating a full admin workflow.
- The UI uses POST streaming rather than native `EventSource` because the request body includes the user message and conversation ID.

## Error Handling Decisions

- Missing LLM configuration returns a user-visible hint to set `OPENAI_API_KEY`.
- MCP tool listing has local fallback schemas, but actual tool execution still requires the MCP service to be running.
- Unsupported or weakly matched questions are routed to insufficient-evidence behavior instead of forcing citations from unrelated chunks.
- Local health endpoints allow each service to be checked independently.

## Non-Goals

- Production authentication, SSO, RBAC, tenant isolation, or document-level permissions.
- Production deployment automation, secrets management, monitoring, tracing, or alerting.
- Large-scale ingestion, document versioning, or policy owner approval workflows.
- A legally authoritative HR decision system.

## Extension Points

- Replace the default LLM provider by changing `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `LLM_MODEL`.
- Add additional MCP tools in `mcp-server/mcp_server/main.py`.
- Extend persistence in `backend/app/database.py`.
- Add policy metadata, versioning, or authorization attributes during ingestion.
- Add regression evaluations for known questions and expected citations.
