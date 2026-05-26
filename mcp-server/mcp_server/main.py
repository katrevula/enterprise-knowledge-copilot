from __future__ import annotations

import contextlib
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from .config import FEEDBACK_DB
from .feedback_store import FeedbackStore
from .knowledge_base import KnowledgeBase

knowledge_base = KnowledgeBase()
feedback_store = FeedbackStore(FEEDBACK_DB)

mcp = FastMCP(
    "Enterprise Knowledge Copilot MCP Server",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def search_hr_knowledge_base(query: str, top_k: int = 5) -> dict[str, Any]:
    """Search synthetic HR policies and return ranked excerpts with source metadata."""
    return knowledge_base.search(query=query, top_k=top_k)


@mcp.tool()
def get_policy_excerpt(source_id: str, chunk_id: str) -> dict[str, Any]:
    """Return the exact source excerpt for a policy chunk."""
    return knowledge_base.get_excerpt(source_id=source_id, chunk_id=chunk_id)


@mcp.tool()
def list_policy_resources() -> dict[str, Any]:
    """List available HR policy resources."""
    return knowledge_base.list_resources()


@mcp.tool()
def record_feedback(message_id: str, rating: str, comment: str | None = None) -> dict[str, Any]:
    """Record user feedback for a generated assistant message."""
    if rating not in {"up", "down"}:
        return {"ok": False, "error": "rating must be 'up' or 'down'"}
    stored = feedback_store.record(message_id=message_id, rating=rating, comment=comment)
    return {"ok": True, **stored}


async def health(_: Any) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": "remote-mcp-knowledge-server",
            "transport": "streamable-http",
            "mcp_path": "/mcp",
        }
    )


@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    async with mcp.session_manager.run():
        yield


app = Starlette(
    routes=[
        Route("/health", endpoint=health),
        Mount("/", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)

