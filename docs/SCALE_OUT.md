# Scale-Out Considerations

The current implementation is a local proof of concept. This document outlines how the architecture should evolve for larger datasets, more users, stronger governance, and production operations.

## Production Service Model

| Area | POC | Production Direction |
| --- | --- | --- |
| Frontend | Vite dev server | Built static app behind CDN or internal web platform. |
| API gateway | Single FastAPI process | Horizontally scaled service behind a load balancer. |
| MCP server | Single local service | Independently deployed service with auth, audit, and rate limiting. |
| Relational storage | SQLite | Managed relational database with backups and retention controls. |
| Vector storage | Local Chroma | Managed or clustered vector/search platform. |
| Secrets | `.env` | Secret manager with rotation and least-privilege access. |

## Larger Corpus

- Move ingestion into a repeatable pipeline.
- Track document version, source owner, effective date, and access policy.
- Store chunk-level metadata for authorization and audit.
- Support incremental indexing instead of full rebuilds.
- Add retrieval evaluation sets with expected source documents and acceptable answer criteria.

## More Users

- Run the gateway and MCP server as independent services.
- Add request timeouts, rate limits, retries, and circuit breakers.
- Move long-running ingestion outside request-serving processes.
- Use structured logs and correlation IDs across UI, gateway, MCP, and LLM calls.
- Store conversations and feedback in a production database.

## Governance And Security

- Add SSO and user identity propagation from UI to gateway to MCP tools.
- Enforce document-level authorization before retrieval results are returned.
- Maintain immutable audit logs for user question, tool calls, source IDs, and final answer metadata.
- Define data retention and deletion workflows.
- Review hosted LLM provider configuration against organizational policy.
- Add redaction or policy checks if real user-entered sensitive data is in scope.

## Reliability And Observability

Track at minimum:

- Chat request latency by stage: gateway, LLM planning, MCP retrieval, final generation.
- Tool-call success and failure rates.
- Retrieval hit rate and insufficient-evidence rate.
- Citation count and average relevance score.
- LLM provider errors and rate limits.
- Frontend stream errors and feedback submission failures.

Recommended production tooling includes distributed tracing, metrics dashboards, alerting, log aggregation, and a regression evaluation job.

## Multi-MCP Expansion

The gateway can be extended to connect to multiple MCP servers. A production deployment could separate tools by domain, such as HR policies, IT service management, benefits, onboarding workflows, and incident systems. Each MCP server should own its authorization model and expose tool schemas that can be reviewed independently.

## Evaluation Roadmap

- Build a test set of representative policy questions.
- Record expected source documents and answer requirements.
- Evaluate retrieval recall before generation.
- Evaluate final answers for citation support and unsupported claims.
- Track regressions when documents, prompts, models, or embedding settings change.
