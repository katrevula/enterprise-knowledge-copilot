# Prompt And Tools

## System Prompt

The gateway uses a system prompt that tells the model to behave as an internal HR policy assistant, answer only from MCP-retrieved knowledge, cite relevant policies, and admit when the current knowledge base does not contain enough information.

## MCP Tools

The remote MCP server exposes:

- `search_hr_knowledge_base(query, top_k)`: semantic search over HR policy chunks.
- `get_policy_excerpt(source_id, chunk_id)`: exact source lookup.
- `list_policy_resources()`: available synthetic policy documents.
- `record_feedback(message_id, rating, comment?)`: answer feedback capture.

## Tool Loop

1. FastAPI lists MCP tools and converts them to OpenAI-compatible function schemas.
2. FastAPI sends the user message and tool schemas to Groq.
3. Groq may return a tool call.
4. FastAPI executes the tool call through the MCP Streamable HTTP client.
5. FastAPI sends the tool result back to Groq.
6. Groq generates the final grounded response.

If the model does not request a tool, FastAPI performs a fallback `search_hr_knowledge_base` call before final generation. This improves reliability for policy questions.

## AI Interaction Improvements

- Grounding through MCP retrieval.
- Citations under every supported answer.
- Insufficient-evidence handling for unsupported questions.
- Visible tool-call/status activity in the UI.
- User feedback controls for answer quality.

