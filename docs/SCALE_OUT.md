# Scale-Out Considerations

## Larger Datasets

For larger corpora, move ingestion to a scheduled pipeline, add document versioning, use chunk-level access metadata, and consider a managed vector database.

## More Users

Deploy the FastAPI gateway and MCP server independently behind load balancers. Use a production database for conversations, feedback, and audits.

## Enterprise Governance

Add SSO, RBAC, per-document authorization, policy owner approval workflows, data retention rules, and audit export.

## Multiple MCP Servers

The same FastAPI MCP host can connect to additional remote MCP servers for HR, IT service management, onboarding systems, legal policies, and incident tooling.

## Monitoring And Evaluation

Track latency, tool-call success, retrieval hit rate, unanswered questions, feedback quality, and LLM/provider errors. Add a regression set of policy questions with expected source citations.

