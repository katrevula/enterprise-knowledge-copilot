# Assumptions And Limitations

This document defines the boundaries of the current proof of concept so reviewers can evaluate it against the intended scope.

## Assumptions

| Assumption | Impact |
| --- | --- |
| A valid OpenAI-compatible LLM API key is available. | Chat generation requires a hosted model call. |
| The selected model supports OpenAI-compatible tool calling. | The first LLM pass can request MCP tools. |
| The app runs locally as three services. | Local ports `5173`, `8000`, and `8001` must be available. |
| The policy corpus is synthetic Markdown content. | No production data ingestion or access control is included. |
| Chroma and the embedding model can run on standard developer hardware. | Ingestion may download model files on first run. |

## Included

- React chat UI with streaming answer rendering.
- FastAPI gateway for chat orchestration, persistence, and MCP tool execution.
- Remote MCP knowledge server over Streamable HTTP.
- Chroma semantic retrieval over eight synthetic HR policy documents.
- Local SQLite persistence for conversations, feedback, and audit metadata.
- Citations, relevance filtering, insufficient-evidence handling, and feedback controls.
- macOS and Windows setup guidance.

## Not Included

- Production authentication, SSO, RBAC, tenant isolation, or document-level authorization.
- Production secrets management.
- Production deployment, autoscaling, tracing, metrics, alerting, or incident response.
- Document owner workflows, approvals, retention policy, or immutable audit logging.
- Large-corpus ingestion, incremental indexing, or document versioning.
- Legal or HR decision authority.

## Functional Limitations

- The LLM may still produce an imperfect summary of retrieved text.
- Retrieval quality depends on chunking, embedding model behavior, and corpus quality.
- The relevance threshold is a practical guardrail, not a formal confidence guarantee.
- The UI does not currently support conversation search, admin feedback review, or source-document browsing.
- Feedback is stored but not used automatically for model tuning or retrieval evaluation.

## Operational Limitations

- SQLite is suitable for local evaluation but not multi-node production traffic.
- Chroma is used locally and is not configured for high availability.
- The frontend is a Vite development app unless built and served separately.
- Hosted LLM rate limits can interrupt demos.
- Runtime state under `storage/` can be deleted and regenerated, but conversation history would be lost.

## Recommended Next Steps

- Add end-to-end tests for chat streaming and citation behavior.
- Add retrieval evaluation cases with expected source IDs.
- Add an admin review screen for feedback.
- Add authorization metadata to chunks during ingestion.
- Replace local storage with managed production services for any real deployment.
