from __future__ import annotations

import json
import time
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import EnterpriseCopilotAgent
from .config import settings
from .database import ConversationStore
from .llm_client import LLMClient, LLMConfigurationError
from .mcp_client import MCPToolClient
from .models import ChatStreamRequest, ConversationResponse, FeedbackRequest

app = FastAPI(title="Enterprise Knowledge Copilot Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ConversationStore(settings.database_url)


def sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "fastapi-ai-gateway",
        "llm_model": settings.llm_model,
        "llm_base_url": settings.openai_base_url,
        "mcp_server_url": settings.mcp_server_url,
        "llm_configured": bool(settings.openai_api_key),
    }


@app.post("/api/chat/stream")
async def chat_stream(payload: ChatStreamRequest) -> StreamingResponse:
    conversation_id = store.ensure_conversation(payload.conversation_id)
    user_message_id = store.add_message(conversation_id, "user", payload.message)

    async def event_generator():
        started_at = time.perf_counter()
        answer = ""
        citations: list[dict[str, Any]] = []
        status = "error"

        yield sse(
            "status",
            {
                "state": "received",
                "conversation_id": conversation_id,
                "user_message_id": user_message_id,
            },
        )

        try:
            history = store.get_messages(conversation_id)
            agent = EnterpriseCopilotAgent(LLMClient(), MCPToolClient())
            async for item in agent.stream_response(payload.message, history):
                event = item["event"]
                data = item["data"]
                if event == "token":
                    answer += data.get("text", "")
                elif event == "citations":
                    citations = data.get("citations", [])
                elif event == "done":
                    answer = data.get("answer", answer)
                    citations = data.get("citations", citations)
                    status = data.get("status", "grounded")
                yield sse(event, data)

            assistant_message_id = store.add_message(
                conversation_id,
                "assistant",
                answer,
                citations,
            )
            latency_ms = round((time.perf_counter() - started_at) * 1000)
            store.add_audit_event(
                "chat_completed",
                {"status": status, "latency_ms": latency_ms, "citation_count": len(citations)},
                conversation_id,
            )
            yield sse(
                "complete",
                {
                    "conversation_id": conversation_id,
                    "message_id": assistant_message_id,
                    "status": status,
                    "latency_ms": latency_ms,
                },
            )
        except LLMConfigurationError as exc:
            yield sse(
                "error",
                {
                    "message": str(exc),
                    "hint": "Set OPENAI_API_KEY in .env. Groq Free Plan keys work with this project.",
                },
            )
        except Exception as exc:
            store.add_audit_event(
                "chat_failed",
                {"error": str(exc)},
                conversation_id,
            )
            yield sse(
                "error",
                {
                    "message": "The assistant could not complete the request.",
                    "detail": str(exc),
                },
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str) -> dict[str, Any]:
    return {
        "conversation_id": conversation_id,
        "messages": store.get_messages(conversation_id, limit=100),
    }


@app.post("/api/feedback")
async def feedback(payload: FeedbackRequest) -> dict[str, Any]:
    feedback_id = store.add_feedback(payload.message_id, payload.rating, payload.comment)
    try:
        await MCPToolClient().call_tool(
            "record_feedback",
            {
                "message_id": payload.message_id,
                "rating": payload.rating,
                "comment": payload.comment,
            },
        )
    except Exception:
        store.add_audit_event(
            "feedback_mcp_record_failed",
            {"message_id": payload.message_id, "rating": payload.rating},
        )
    return {"ok": True, "feedback_id": feedback_id}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Enterprise Knowledge Copilot FastAPI Gateway"}

