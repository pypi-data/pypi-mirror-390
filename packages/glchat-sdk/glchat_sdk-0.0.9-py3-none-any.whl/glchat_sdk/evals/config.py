"""GLChat configuration module.

This module provides configuration management for GLChat evaluation,
including validation and environment variable support.
Code Quality Requirement: All functions must enforce maximum 5 lines when possible,
creating separate helper files if functions cannot be broken down further.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, field_validator

from glchat_sdk.evals.constant import (
    GLChatDefaults,
    GLChatFieldNames,
    GLChatSearchTypes,
)


class GLChatConfig(BaseModel):
    """Configuration for GLChat evaluation.

    This class defines all configuration parameters needed for GLChat evaluation,
    including API credentials, model settings, and optional features.

    Attributes:
        base_url (str): GLChat API base URL
        api_key (str): GLChat API key
        chatbot_id (str): GLChat chatbot identifier
        model_name (str): Model to use for evaluation
        username (str): Username for GLChat evaluation
        enable_pii (bool): Enable PII anonymization/deanonymization
        search_type (str): Search type configuration
        include_states (bool): Whether to include states in the response
        expiry_days (int | None): Number of days for shared conversation expiry (None for no expiry)
    """

    # Required fields (with environment variable fallback)
    base_url: str | None = Field(
        default=None, description="GLChat API base URL (falls back to GLCHAT_BASE_URL env var)"
    )
    api_key: str | None = Field(
        default=None, description="GLChat API key (falls back to GLCHAT_API_KEY env var)"
    )
    chatbot_id: str = Field(..., description="GLChat chatbot identifier")

    # Optional fields with defaults
    username: str = Field(
        default=GLChatDefaults.USERNAME, description="Username for GLChat evaluation"
    )
    model_name: str | None = Field(default=None, description="Model to use for evaluation")
    enable_pii: bool = Field(default=False, description="Enable PII anonymization/deanonymization")
    search_type: str = Field(
        default=GLChatSearchTypes.NORMAL,
        description="Search type: normal, search, web, deep_research, essentials_deep_research, "
        "comprehensive_deep_research",
    )
    include_states: bool = Field(
        default=True, description="Whether to include states in the response"
    )
    expiry_days: int | None = Field(
        default=None,
        description="Number of days for shared conversation expiry (None for no expiry)",
    )

    @field_validator(GLChatFieldNames.BASE_URL)
    @classmethod
    def validate_base_url(cls, v: str | None) -> str | None:
        """Validate base URL format."""
        if v is not None and not v.startswith("https://"):
            raise ValueError("base_url must be a valid HTTPS URL")
        return v

    @field_validator(GLChatFieldNames.API_KEY)
    @classmethod
    def validate_api_key(cls, v: str | None) -> str | None:
        """Validate API key is not empty."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("api_key cannot be empty")
        return v.strip() if v else None

    @field_validator(GLChatFieldNames.CHATBOT_ID)
    @classmethod
    def validate_chatbot_id(cls, v: str) -> str:
        """Validate chatbot ID is not empty."""
        if not v or not v.strip():
            raise ValueError("chatbot_id cannot be empty")
        return v.strip()

    @field_validator(GLChatFieldNames.SEARCH_TYPE)
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Validate search type is valid."""
        valid_types = [
            value
            for key, value in vars(GLChatSearchTypes).items()
            if not key.startswith("_") and isinstance(value, str)
        ]
        if v not in valid_types:
            raise ValueError(f"search_type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("expiry_days")
    @classmethod
    def validate_expiry_days(cls, v: int | None) -> int | None:
        """Validate expiry days is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("expiry_days must be a positive integer or None")
        return v


class HTTPMessageRequest(BaseModel):
    """Request model for HTTP message creation with file uploads.

    This model is specifically designed for the create_message_http function
    and includes additional fields needed for HTTP requests with file uploads.
    """

    # Core message fields
    chatbot_id: str
    message: str
    username: str
    conversation_id: str

    # Optional message fields
    chat_history: str | None = None
    model_name: str | None = None
    parent_id: str | None = None
    connectors: str | None = None

    # Boolean flags
    anonymize_lm: bool = False
    include_states: bool = True

    # Search configuration
    search_type: str = "normal"

    # File uploads
    files: list[Any] = Field(default=[], description="List of file objects (BinaryIO)")


@dataclass
class GLChatResponse:
    """Response dataclass for GLChat API responses.

    This dataclass encapsulates all the data returned from GLChat API calls,
    making it easier to work with than long tuples.

    Attributes:
        final_response: The main response text from the chatbot
        media_mapping_data: Dictionary containing media mapping information
        context_data: Additional context data from the response
        assistant_message_id: ID of the assistant message
    """

    final_response: str
    media_mapping_data: dict | None = None
    context_data: str | None = None
    assistant_message_id: str | None = None
