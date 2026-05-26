# Assumptions And Limitations

## Assumptions

- A Groq Free Plan API key is available.
- The selected Groq model supports OpenAI-compatible tool calling.
- The app runs as three local services during the POC: MCP server, FastAPI gateway, and React dev server.
- The dataset is synthetic HR policy content committed under `data/hr_policies/`.
- Chroma and the embedding model can run on standard developer hardware.

## Limitations

- Free hosted LLM APIs have rate limits and may return 429 responses.
- The synthetic dataset is intentionally small.
- The POC does not implement SSO, RBAC, tenant isolation, or document-level authorization.
- The UI streams responses over a POST `fetch()` stream rather than native `EventSource`, because `EventSource` cannot send POST bodies.
- SQLite is used for local persistence and is not intended for multi-node production traffic.

## Improvements With More Time

- Add authentication and role-based policy access.
- Add automated retrieval evaluation and hallucination tests.
- Add admin screens for feedback review.
- Add multiple MCP servers for HR, IT, legal, and incident management.
- Add production tracing, metrics, alerting, and immutable audit logs.

