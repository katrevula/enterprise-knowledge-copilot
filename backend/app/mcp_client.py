from __future__ import annotations

import json
from typing import Any

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

from .config import settings


FALLBACK_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_hr_knowledge_base",
            "description": "Search synthetic HR policies and return ranked excerpts with source metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy_excerpt",
            "description": "Return the exact source excerpt for a policy chunk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "chunk_id": {"type": "string"},
                },
                "required": ["source_id", "chunk_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_policy_resources",
            "description": "List available HR policy resources.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": "Record user feedback for a generated assistant message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "string"},
                    "rating": {"type": "string", "enum": ["up", "down"]},
                    "comment": {"type": "string"},
                },
                "required": ["message_id", "rating"],
            },
        },
    },
]


class MCPToolClient:
    def __init__(self, server_url: str = settings.mcp_server_url) -> None:
        self.server_url = server_url

    async def list_openai_tools(self) -> list[dict[str, Any]]:
        try:
            async with streamable_http_client(self.server_url) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    tools = []
                    for tool in response.tools:
                        tools.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": tool.name,
                                    "description": tool.description or "",
                                    "parameters": tool.inputSchema
                                    or {"type": "object", "properties": {}},
                                },
                            }
                        )
                    return tools or FALLBACK_TOOL_SCHEMAS
        except Exception:
            return FALLBACK_TOOL_SCHEMAS

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with streamable_http_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=arguments)
                return self._parse_result(name, result)

    def _parse_result(self, name: str, result: Any) -> dict[str, Any]:
        structured = getattr(result, "structuredContent", None)
        if structured:
            return {"tool": name, "result": structured}

        content_items = getattr(result, "content", []) or []
        text_blocks = []
        for item in content_items:
            if isinstance(item, types.TextContent):
                text_blocks.append(item.text)

        joined = "\n".join(text_blocks).strip()
        if joined:
            try:
                return {"tool": name, "result": json.loads(joined)}
            except json.JSONDecodeError:
                return {"tool": name, "result": {"text": joined}}

        return {"tool": name, "result": {}, "is_error": bool(getattr(result, "isError", False))}

