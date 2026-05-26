# Design Rationale

## Why FastAPI

FastAPI provides clear request/response contracts, async streaming, OpenAPI docs, and straightforward Python integration with the OpenAI-compatible client, MCP SDK, Chroma, and SQLite.

## Why Remote MCP

MCP is used as the standardized tool/resource layer. The knowledge server is separate from the AI Gateway to show an enterprise-ready boundary where additional tools, policy stores, or access controls can be added without rewriting the UI.

## Why FastAPI Controls The Tool Loop

Groq is hosted and should not be expected to reach a local MCP endpoint. FastAPI therefore acts as the MCP host/client. The LLM decides when tools are useful; FastAPI executes the MCP calls and returns the results to the LLM.

## Why Synthetic HR Data

The assignment asks for public, synthetic, or de-identified data. Synthetic HR policies closely match the problem statement while avoiding private or company-confidential information.

## Why Chroma

Chroma gives a local persistent vector index that runs on standard developer hardware. It is enough for the POC while still demonstrating semantic retrieval and citation metadata.

## Key Tradeoffs

- A hosted free LLM avoids local model installation, but the app must handle rate limits.
- The MCP split adds complexity, but it better demonstrates enterprise integration boundaries.
- SQLite is sufficient for a POC; production would use a managed database.

