from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from .config import settings
from .llm_client import LLMClient
from .mcp_client import MCPToolClient

SYSTEM_PROMPT = """You are Enterprise Knowledge Copilot, an internal HR policy assistant.
Answer only from information retrieved through the MCP HR knowledge tools.
If the available sources do not answer the question, say that there is not enough information in the current knowledge base.
Use clear, concise language for employees. Do not invent policy details.
When sources are available, mention the relevant policy names or sections in the answer."""


class EnterpriseCopilotAgent:
    def __init__(self, llm: LLMClient, mcp: MCPToolClient) -> None:
        self.llm = llm
        self.mcp = mcp

    async def stream_response(
        self,
        user_message: str,
        history: list[dict[str, Any]],
    ) -> AsyncIterator[dict[str, Any]]:
        yield {"event": "status", "data": {"state": "planning", "message": "Preparing tool context"}}

        tools = await self.mcp.list_openai_tools()
        messages = self._build_initial_messages(user_message, history)
        first_response = await self.llm.plan_tool_calls(messages=messages, tools=tools)
        assistant_message = first_response.choices[0].message
        tool_calls = list(getattr(assistant_message, "tool_calls", None) or [])

        tool_results: list[dict[str, Any]] = []
        final_messages = list(messages)

        if tool_calls:
            final_messages.append(self._assistant_tool_message(assistant_message))
            for tool_call in tool_calls:
                name = tool_call.function.name
                arguments = self._safe_json(tool_call.function.arguments)
                yield {
                    "event": "tool_call",
                    "data": {"name": name, "arguments": self._safe_tool_metadata(arguments)},
                }
                tool_result = self._filter_low_relevance_results(
                    await self.mcp.call_tool(name, arguments)
                )
                tool_results.append(tool_result)
                final_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
        else:
            yield {
                "event": "tool_call",
                "data": {
                    "name": "search_hr_knowledge_base",
                    "arguments": {"query": user_message, "top_k": 5, "fallback": True},
                },
            }
            tool_result = self._filter_low_relevance_results(
                await self.mcp.call_tool(
                    "search_hr_knowledge_base",
                    {"query": user_message, "top_k": 5},
                )
            )
            tool_results.append(tool_result)
            final_messages.append(
                {
                    "role": "system",
                    "content": "MCP retrieval result:\n"
                    + json.dumps(tool_result, ensure_ascii=False),
                }
            )

        citations = self._extract_citations(tool_results)
        if not citations:
            final_messages.append(
                {
                    "role": "system",
                    "content": "No relevant MCP citations were found. State that the current knowledge base does not contain enough information.",
                }
            )

        yield {"event": "status", "data": {"state": "generating", "message": "Generating grounded answer"}}

        answer_parts: list[str] = []
        async for token in self.llm.stream_final_answer(final_messages):
            answer_parts.append(token)
            yield {"event": "token", "data": {"text": token}}

        status = "grounded" if citations else "insufficient_evidence"
        yield {"event": "citations", "data": {"citations": citations}}
        yield {
            "event": "done",
            "data": {
                "answer": "".join(answer_parts).strip(),
                "citations": citations,
                "status": status,
            },
        }

    def _build_initial_messages(
        self,
        user_message: str,
        history: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for item in history[-8:]:
            role = item.get("role")
            if role in {"user", "assistant"}:
                messages.append({"role": role, "content": item.get("content", "")})
        messages.append({"role": "user", "content": user_message})
        return messages

    def _assistant_tool_message(self, assistant_message: Any) -> dict[str, Any]:
        tool_calls = []
        for tool_call in getattr(assistant_message, "tool_calls", []) or []:
            tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            )
        return {
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": tool_calls,
        }

    def _safe_json(self, raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _safe_tool_metadata(self, arguments: dict[str, Any]) -> dict[str, Any]:
        allowed = {}
        for key in ("query", "top_k", "source_id", "chunk_id", "rating"):
            if key in arguments:
                allowed[key] = arguments[key]
        return allowed

    def _filter_low_relevance_results(self, tool_result: dict[str, Any]) -> dict[str, Any]:
        result = tool_result.get("result", {})
        if tool_result.get("tool") != "search_hr_knowledge_base" or not isinstance(result, dict):
            return tool_result

        results = result.get("results")
        if not isinstance(results, list):
            return tool_result

        filtered = []
        for item in results:
            if not isinstance(item, dict):
                continue
            score = item.get("score")
            if isinstance(score, (int, float)) and float(score) >= settings.min_relevance_score:
                filtered.append(item)

        return {
            **tool_result,
            "result": {
                **result,
                "results": filtered,
                "min_relevance_score": settings.min_relevance_score,
            },
        }

    def _extract_citations(self, tool_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for tool_result in tool_results:
            result = tool_result.get("result", {})
            if isinstance(result, dict) and "results" in result:
                for item in result.get("results", []):
                    source_key = (item.get("source_id", ""), item.get("chunk_id", ""))
                    if not source_key[0] or source_key in seen:
                        continue
                    seen.add(source_key)
                    citations.append(
                        {
                            "source_id": item.get("source_id", ""),
                            "chunk_id": item.get("chunk_id", ""),
                            "title": item.get("title", "Untitled policy"),
                            "section": item.get("section", ""),
                            "excerpt": item.get("excerpt", ""),
                            "score": item.get("score"),
                        }
                    )
            elif isinstance(result, dict) and result.get("found"):
                source_key = (result.get("source_id", ""), result.get("chunk_id", ""))
                if source_key[0] and source_key not in seen:
                    seen.add(source_key)
                    citations.append(
                        {
                            "source_id": result.get("source_id", ""),
                            "chunk_id": result.get("chunk_id", ""),
                            "title": result.get("title", "Untitled policy"),
                            "section": result.get("section", ""),
                            "excerpt": result.get("excerpt", ""),
                            "score": None,
                        }
                    )
        return citations[:5]
