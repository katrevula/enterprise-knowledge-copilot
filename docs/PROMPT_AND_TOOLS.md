# Prompt And Tools

This document describes how the gateway prompts the LLM, exposes MCP tools, and converts tool results into grounded answers.

## System Prompt Contract

The backend system prompt is defined in `backend/app/agent.py`. It instructs the model to:

- Act as an internal HR policy assistant.
- Answer only from MCP-retrieved information.
- Say when the current knowledge base does not contain enough evidence.
- Avoid inventing policy details.
- Mention relevant policy names or sections when sources are available.

The prompt is intentionally short. The strongest grounding control is not prompt wording alone; it is the runtime path that retrieves source chunks, filters low-relevance matches, and passes the retained evidence into final generation.

## Tool Inventory

The remote MCP server exposes these tools:

| Tool | Inputs | Output | Purpose |
| --- | --- | --- | --- |
| `search_hr_knowledge_base` | `query`, `top_k` | Ranked excerpts with `source_id`, `chunk_id`, title, section, score, and distance. | Primary semantic retrieval path. |
| `get_policy_excerpt` | `source_id`, `chunk_id` | Exact excerpt or `found: false`. | Exact source lookup by citation metadata. |
| `list_policy_resources` | none | Available policy resources and chunk counts. | Resource discovery and debugging. |
| `record_feedback` | `message_id`, `rating`, optional `comment` | Stored feedback metadata. | Captures answer quality feedback through MCP. |

## Tool Loop

1. FastAPI requests tool schemas from the MCP server.
2. The schemas are converted to OpenAI-compatible function definitions.
3. FastAPI sends recent conversation history, the latest user question, and tool schemas to the LLM.
4. If the LLM requests a tool, FastAPI executes that call through the MCP Streamable HTTP client.
5. If the LLM does not request a tool, FastAPI performs a fallback `search_hr_knowledge_base` call for the user question.
6. Search results below `MIN_RELEVANCE_SCORE` are filtered out by the gateway.
7. Tool results are sent back to the LLM as grounded context.
8. The final answer is streamed to the UI.

## Relevance And Insufficient Evidence

Vector search always returns the nearest chunks if the index is non-empty, even when the question is unrelated to the corpus. To avoid presenting unrelated chunks as support, the gateway filters search results using `MIN_RELEVANCE_SCORE`.

If no citation remains after filtering:

- The assistant status is `insufficient_evidence`.
- The final prompt explicitly tells the model to say the current knowledge base does not contain enough information.
- The UI receives an empty citation list.

The default threshold is `0.45`. It is intentionally configurable because score distributions can change when the corpus, embedding model, or chunking strategy changes.

## Streaming Event Contract

`POST /api/chat/stream` emits SSE-formatted blocks over a POST response stream:

| Event | Data |
| --- | --- |
| `status` | Current lifecycle state and optional message. |
| `tool_call` | Tool name and safe argument metadata. |
| `token` | Incremental answer text. |
| `citations` | Final citation list. |
| `done` | Final answer text, citations, and answer status. |
| `complete` | Stored message ID, conversation ID, status, and latency. |
| `error` | Error message plus optional hint or detail. |

The UI currently renders `status`, `tool_call`, `token`, `citations`, `complete`, and `error`.

## Prompt And Tool Limitations

- The LLM can still summarize retrieved evidence incorrectly.
- Retrieval can miss relevant content if chunking or embeddings are insufficient.
- The current implementation does not perform citation-level factual verification after generation.
- The feedback workflow records user ratings but does not yet feed an automated evaluation loop.
