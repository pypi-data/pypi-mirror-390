"""Data models for the GLChat Python client.

This module contains Pydantic models for request and response data structures
used in the GLChat Python client library.

Example:
    >>> request = MessageRequest(
    ...     application_id="your-application-id",
    ...     message="Hello!",
    ...     user_id="user_123"
    ... )
    >>> data = request.model_dump()

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

import warnings

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageRequest(BaseModel):
    """Request model for sending messages to the GLChat API."""

    # Disable pydantic's protected namespace "model_"
    model_config = ConfigDict(protected_namespaces=())

    application_id: str | None = None
    chatbot_id: str | None
    message: str
    parent_id: str | None = None
    source: str | None = None
    quote: str | None = None
    user_id: str | None = None
    conversation_id: str | None = None
    user_message_id: str | None = None
    assistant_message_id: str | None = None
    chat_history: str | None = None
    stream_id: str | None = None
    metadata: str | None = None
    model_name: str | None = None
    anonymize_em: bool | None = None
    anonymize_lm: bool | None = None
    use_cache: bool | None = None
    search_type: str | None = None
    agent_ids: list[str] | None = None
    exclude_events: list[str] | None = None
    stream_message_only: bool | None = None
    exclude_prefix: bool | None = None
    include_states: bool | None = None
    filters: str | None = None


class MessageResponse(BaseModel):
    """Response model for messages from the GLChat API."""

    status: str | None = None
    message: str | None = None
    original: dict | None = None


class ConversationRequest(BaseModel):
    """Request model for creating conversations with the GLChat API."""

    # Disable pydantic's protected namespace "model_"
    model_config = ConfigDict(protected_namespaces=())

    user_id: str
    application_id: str | None = None
    chatbot_id: str | None = None
    title: str | None = None
    model_name: str | None = None
