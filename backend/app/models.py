from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    comment: str | None = Field(default=None, max_length=1000)


class Citation(BaseModel):
    source_id: str
    chunk_id: str
    title: str
    section: str
    excerpt: str
    score: float | None = None


class ConversationMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: str
    citations: list[Citation] = []


class ConversationResponse(BaseModel):
    conversation_id: str
    messages: list[ConversationMessage]

