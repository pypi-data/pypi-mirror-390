"""GLChat utility functions.

This module provides utility functions for GLChat operations including
client creation, response parsing, and HTTP request handling.

Code Quality Requirement: All functions must enforce maximum 5 lines when possible,
creating separate helper files if functions cannot be broken down further.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

import json
from collections.abc import Iterator
from typing import Any

import aiohttp
from gllm_core.utils import LoggerManager

from glchat_sdk import GLChat
from glchat_sdk.evals.config import GLChatConfig, GLChatResponse, HTTPMessageRequest
from glchat_sdk.evals.constant import (
    GeneralKeys,
    GLChatDataTypes,
    GLChatDefaults,
    GLChatEnvVars,
    GLChatFieldNames,
    GLChatHTTPKeys,
    GLChatSSEKeys,
)

logger = LoggerManager().get_logger(__name__)


def create_glchat_client(base_url: str, api_key: str) -> GLChat:
    """Create GLChat client with provided credentials.

    Args:
        base_url (str): GLChat API base URL
        api_key (str): GLChat API key

    Returns:
        GLChat: Configured GLChat client

    Raises:
        ValueError: If credentials are missing
    """
    if not base_url:
        raise ValueError("base_url is required")
    if not api_key:
        raise ValueError("api_key is required")

    return GLChat(base_url=base_url, api_key=api_key)


def resolve_config_from_env(config: GLChatConfig) -> GLChatConfig:
    """Resolve missing config values from environment variables.

    Args:
        config (GLChatConfig): GLChat configuration object

    Returns:
        GLChatConfig: Updated configuration with resolved values

    Raises:
        ValueError: If required values cannot be resolved
    """
    import os

    # Create updated config without mutating original
    updated_config = config.model_copy(
        update={
            GLChatFieldNames.BASE_URL: config.base_url or os.getenv(GLChatEnvVars.GLCHAT_BASE_URL),
            GLChatFieldNames.API_KEY: config.api_key or os.getenv(GLChatEnvVars.GLCHAT_API_KEY),
        }
    )

    if not updated_config.base_url:
        raise ValueError("GLCHAT_BASE_URL environment variable is required")
    if not updated_config.api_key:
        raise ValueError("GLCHAT_API_KEY environment variable is required")

    return updated_config


def parse_conversation_response(response: dict[str, Any]) -> str:
    """Parse conversation creation response to extract conversation ID.

    Args:
        response (dict[str, Any]): The API response

    Returns:
        str: The conversation ID
    """
    # Try different possible locations for the conversation ID
    conversation_id = (
        response.get(GLChatFieldNames.ID)
        or response.get(GLChatFieldNames.CONVERSATION_ID)
        or (
            response.get(GLChatFieldNames.CONVERSATION, {}).get(GLChatFieldNames.ID)
            if isinstance(response.get(GLChatFieldNames.CONVERSATION), dict)
            else None
        )
    )

    if not conversation_id:
        raise ValueError(f"No conversation ID found in response: {response}")

    return str(conversation_id)


def _parse_sse_chunk(
    chunk_str: str,
    media_mapping_data: dict,
    context_data: str,
    deanonymized_mapping: dict,
    deanonymized_content: str,
    final_response: str,
    assistant_message_id: str | None,
) -> tuple[dict, str, dict, str, str, str | None]:
    """Parse a single SSE chunk and extract relevant data.

    Args:
        chunk_str (str): The SSE chunk string to parse
        media_mapping_data (dict): Current media mapping data dict
        context_data (str): Current context data string
        deanonymized_mapping (dict): Current deanonymized mapping dict
        deanonymized_content (str): Current deanonymized content string
        final_response (str): Current final response string
        assistant_message_id (str | None): Current assistant message ID

    Returns:
        tuple[dict | None, str | None, dict | None, str | None, str | None, str | None]: A tuple containing updated values:
            (media_mapping_data, context_data, deanonymized_mapping,
            deanonymized_content, final_response, assistant_message_id)
    """
    # Parse the SSE data
    if chunk_str.startswith(GLChatSSEKeys.DATA_PREFIX):
        try:
            # Extract JSON data after "data:"
            json_str = chunk_str[len(GLChatSSEKeys.DATA_PREFIX) :]  # Remove "data:" prefix
            data = json.loads(json_str)

            # Always look for media_mapping and context data
            if data.get(GLChatFieldNames.STATUS) == GLChatDataTypes.DATA:
                message_data = data.get(GLChatFieldNames.MESSAGE, "")
                if isinstance(message_data, str):
                    try:
                        message_json = json.loads(message_data)
                        if (
                            message_json.get(GLChatFieldNames.DATA_TYPE)
                            == GLChatDataTypes.MEDIA_MAPPING
                        ):
                            media_mapping_data = message_json.get(GLChatFieldNames.DATA_VALUE, {})
                        if message_json.get(GLChatFieldNames.DATA_TYPE) == GLChatDataTypes.STATES:
                            states_data = message_json.get(GLChatFieldNames.DATA_VALUE, {})
                            context_data = states_data.get(GLChatFieldNames.CONTEXT, "")
                    except json.JSONDecodeError:
                        pass

            # Look for deanonymized_data type
            if data.get(GLChatFieldNames.STATUS) == GLChatDataTypes.DATA:
                message_data = data.get(GLChatFieldNames.MESSAGE, "")
                if isinstance(message_data, str):
                    try:
                        message_json = json.loads(message_data)
                        if (
                            message_json.get(GLChatFieldNames.DATA_TYPE)
                            == GLChatDataTypes.DEANONYMIZED_DATA
                        ):
                            deanonymized_data = message_json.get(GLChatFieldNames.DATA_VALUE, {})
                            ai_message = deanonymized_data.get(GLChatFieldNames.AI_MESSAGE, {})
                            deanonymized_content = ai_message.get(
                                GLChatFieldNames.DEANONYMIZED_CONTENT, ""
                            )
                            deanonymized_mapping = deanonymized_data.get(
                                GLChatFieldNames.DEANONYMIZED_MAPPING, {}
                            )
                    except json.JSONDecodeError:
                        pass

            if data.get(GLChatFieldNames.STATUS) == GLChatDataTypes.RESPONSE:
                final_response = data.get(GLChatFieldNames.MESSAGE, "")

            if data.get(GLChatFieldNames.STATUS) == GLChatDataTypes.DATA:
                assistant_message_id = data.get(GLChatDataTypes.ASSISTANT_MESSAGE_ID)

        except json.JSONDecodeError:
            pass

    # Check for UNKERR error
    if not final_response and GLChatSSEKeys.UNKERR_ERROR in chunk_str:
        final_response = "Error UNKERR encountered in glchat response"

    return (
        media_mapping_data,
        context_data,
        deanonymized_mapping,
        deanonymized_content,
        final_response,
        assistant_message_id,
    )


def _process_final_response(
    final_response: str,
    media_mapping_data: dict,
    context_data: str,
    deanonymized_mapping: dict,
    deanonymized_content: str,
    is_anonymize_lm: bool,
) -> tuple[str, dict | None, str | None]:
    """Process the final response with mappings and deanonymization.

    Args:
        final_response (str): The final response text
        media_mapping_data (dict): Media mapping data dict
        context_data (str): Context data string
        deanonymized_mapping (dict): Deanonymized mapping dict
        deanonymized_content (str): Deanonymized content string
        is_anonymize_lm (bool): Whether to use deanonymized content

    Returns:
        tuple[str, dict | None, str | None]: A tuple containing
            (final_response, media_mapping_data_or_None, context_data_or_None)
    """
    # Use deanonymized content if requested and available
    if is_anonymize_lm and deanonymized_content:
        final_response = deanonymized_content
        # Apply deanonymized mapping to the final response
        if deanonymized_mapping and isinstance(deanonymized_mapping, dict):
            for key, value in deanonymized_mapping.items():
                final_response = final_response.replace(key, value)

    # Return None for media_mapping_data if no media mapping was found
    if not media_mapping_data:
        media_mapping_data = None

    if not context_data:
        context_data = None

    if context_data:
        if deanonymized_mapping and isinstance(deanonymized_mapping, dict):
            for key, value in deanonymized_mapping.items():
                context_data = context_data.replace(key, value)
                final_response = final_response.replace(key, value)
        if media_mapping_data and isinstance(media_mapping_data, dict):
            for key, value in media_mapping_data.items():
                context_data = context_data.replace(key, value)
                final_response = final_response.replace(key, value)

    return final_response, media_mapping_data, context_data


def parse_response(  # noqa: PLR0912
    responses: Iterator[bytes], is_anonymize_lm: bool = False
) -> GLChatResponse:
    """Parse Server-Sent Events (SSE) response from the chatbot.

    Args:
        responses (Iterator[bytes]): An iterator of bytes containing SSE data chunks
        is_anonymize_lm (bool): Whether to look for deanonymized content

    Returns:
        GLChatResponse: A response object containing all parsed data
    """

    final_response = ""
    media_mapping_data = {}
    context_data = ""
    deanonymized_mapping = {}
    deanonymized_content = ""
    assistant_message_id = None

    for chunk in responses:
        chunk_str = chunk.decode(GLChatDefaults.UTF8_ENCODING)
        (
            media_mapping_data,
            context_data,
            deanonymized_mapping,
            deanonymized_content,
            final_response,
            assistant_message_id,
        ) = _parse_sse_chunk(
            chunk_str,
            media_mapping_data,
            context_data,
            deanonymized_mapping,
            deanonymized_content,
            final_response,
            assistant_message_id,
        )

    final_response, media_mapping_data, context_data = _process_final_response(
        final_response,
        media_mapping_data,
        context_data,
        deanonymized_mapping,
        deanonymized_content,
        is_anonymize_lm,
    )

    return GLChatResponse(
        final_response=final_response,
        media_mapping_data=media_mapping_data,
        context_data=context_data,
        assistant_message_id=assistant_message_id,
    )


def parse_sse_string_response(sse_string: str, is_anonymize_lm: bool = False) -> GLChatResponse:
    """Parse a string containing multiple SSE data entries and extract response and media mapping.

    This function replicates the pattern from request_helper.py

    Args:
        sse_string (str): The SSE response string
        is_anonymize_lm (bool): Whether to look for deanonymized content

    Returns:
        GLChatResponse: A response object containing all parsed data
    """
    final_response = ""
    media_mapping_data = {}
    context_data = ""
    deanonymized_mapping = {}
    deanonymized_content = ""
    assistant_message_id = None

    # Split by newlines to get individual chunks
    chunks = sse_string.split("\n")

    for chunk_str in chunks:
        (
            media_mapping_data,
            context_data,
            deanonymized_mapping,
            deanonymized_content,
            final_response,
            assistant_message_id,
        ) = _parse_sse_chunk(
            chunk_str,
            media_mapping_data,
            context_data,
            deanonymized_mapping,
            deanonymized_content,
            final_response,
            assistant_message_id,
        )

    final_response, media_mapping_data, context_data = _process_final_response(
        final_response,
        media_mapping_data,
        context_data,
        deanonymized_mapping,
        deanonymized_content,
        is_anonymize_lm,
    )

    return GLChatResponse(
        final_response=final_response,
        media_mapping_data=media_mapping_data,
        context_data=context_data,
        assistant_message_id=assistant_message_id,
    )


async def create_message_http(
    base_url: str,
    api_key: str,
    request: HTTPMessageRequest,
    *,
    session: aiohttp.ClientSession,
) -> str | None:
    """Create a message with bearer token authentication.

    This function replicates the pattern from glchat_request_helper.py

    Args:
        base_url (str): The base URL for the API
        api_key (str): API key to use as bearer token
        request (HTTPMessageRequest): HTTPMessageRequest containing all message parameters
        session (aiohttp.ClientSession): The HTTP session

    Returns:
        str | None: The response text
    """
    url = f"{base_url.rstrip('/')}/message"

    form_data = aiohttp.FormData()
    form_data.add_field(GLChatFieldNames.CHATBOT_ID, request.chatbot_id)
    form_data.add_field(GLChatFieldNames.MESSAGE, request.message)
    form_data.add_field(GLChatFieldNames.USER_ID, request.username)
    form_data.add_field(GLChatFieldNames.CONVERSATION_ID, request.conversation_id)

    if request.model_name:
        form_data.add_field(GLChatFieldNames.MODEL_NAME, request.model_name)
    form_data.add_field(GLChatFieldNames.ANONYMIZE_LM, str(request.anonymize_lm))
    form_data.add_field(GLChatFieldNames.SEARCH_TYPE, request.search_type)
    form_data.add_field(GLChatFieldNames.INCLUDE_STATES, str(request.include_states))

    if request.connectors:
        form_data.add_field(GLChatFieldNames.CONNECTORS, request.connectors)

    if request.parent_id:
        form_data.add_field(GLChatFieldNames.PARENT_ID, request.parent_id)

    # Add files if any
    if request.files:
        for i, f in enumerate(request.files):
            f.seek(0)
            file_name = getattr(f, "name", None)
            filename = file_name if isinstance(file_name, str) else f"upload_{i}"
            form_data.add_field(GLChatFieldNames.FILES, f, filename=filename)

    headers = {
        GLChatHTTPKeys.AUTHORIZATION: f"{GLChatHTTPKeys.BEARER} {api_key}",
        GeneralKeys.TAG: GeneralKeys.EVALUATION_TAG,
    }

    try:
        async with session.post(url, data=form_data, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {await response.text()}")
            return await response.text()
    except Exception as e:
        logger.error(f"Failed to create message: {str(e)}")
        raise e


async def create_shared_conversation_http(
    base_url: str,
    api_key: str,
    conversation_id: str,
    username: str,
    expiry_days: int | None = None,
    *,
    session: aiohttp.ClientSession,
) -> str | None:
    """Create a shared conversation with bearer token authentication.

    Args:
        base_url (str): The base URL for the API
        api_key (str): API key to use as bearer token
        conversation_id (str): The ID of the conversation to share
        username (str): The username that created the conversation
        expiry_days (int | None): The number of days to share the conversation (None for no expiry)
        session (aiohttp.ClientSession): The session to use for the request

    Returns:
        str | None: The shared conversation ID, or None if creation failed
    """
    url = f"{base_url.rstrip('/')}/conversations/{conversation_id}/share"

    form_data = aiohttp.FormData()
    form_data.add_field(GLChatFieldNames.USER_ID, username)

    if expiry_days is not None:
        form_data.add_field(GLChatFieldNames.EXPIRY_DAYS, str(expiry_days))

    headers = {GLChatHTTPKeys.AUTHORIZATION: f"{GLChatHTTPKeys.BEARER} {api_key}"}

    try:
        async with session.post(url, data=form_data, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {await response.text()}")

            response_data = await response.json()
            shared_conv_id = response_data.get("shared_conversation_id")

            if not shared_conv_id:
                raise Exception(f"No shared conversation ID in response: {response_data}")

            return shared_conv_id
    except Exception as e:
        raise Exception(f"Failed to create shared conversation: {str(e)}") from e
