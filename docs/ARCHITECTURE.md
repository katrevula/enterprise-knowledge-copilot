# Architecture

## System Diagram

```text
React Chat UI
  -> POST /api/chat/stream
  -> FastAPI AI Gateway
     -> Groq OpenAI-compatible chat completions
     -> FastAPI-controlled tool loop
     -> MCP Streamable HTTP client
  -> Remote MCP Knowledge Server /mcp
     -> Chroma vector index
     -> Synthetic HR Markdown documents
```

## Service Boundaries

- React is a UI client. It does not know about Groq, Chroma, or MCP internals.
- FastAPI is the AI Gateway and MCP host/client. It owns sessions, LLM calls, tool execution, and streaming.
- Groq provides the free hosted LLM. It can request tool calls, but it does not directly connect to the MCP server.
- The MCP server exposes tools/resources over Streamable HTTP. It owns retrieval and source metadata.
- Chroma stores local embeddings for synthetic HR policy chunks.

For Mermaid system, sequence, deployment, and responsibility diagrams, see [Flow And Architecture Diagrams](DIAGRAMS.md).

## Request Lifecycle

1. User sends a message from the React chat UI.
2. React opens a POST streaming request to FastAPI.
3. FastAPI sends the message, recent history, and MCP tool schemas to Groq.
4. Groq returns either a tool call or an answer.
5. If a tool call is returned, FastAPI executes it against the remote MCP server over Streamable HTTP.
6. FastAPI sends the MCP result back to Groq.
7. Groq generates a final grounded answer.
8. FastAPI streams status, token, citation, and completion events to React.
9. React renders the answer, citations, and feedback controls.

## Why Streamable HTTP

Streamable HTTP is used because this project models a remote enterprise MCP server. `stdio` is better suited for local subprocess tools, while Streamable HTTP allows separate deployment, network boundaries, service health checks, and future scaling.
