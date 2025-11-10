"""GLChat inference module.

This module provides the core inference functionality for GLChat evaluation,
handling conversation creation, message sending, and response processing.

Code Quality Requirement: All functions must enforce maximum 5 lines when possible,
creating separate helper files if functions cannot be broken down further.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

import asyncio
from typing import Any, BinaryIO

import aiohttp
from gllm_core.utils import LoggerManager
from gllm_core.utils.retry import retry
from gllm_evals.utils.retry_configuration import get_default_retry_config
from gllm_evals.utils.shared_functionality import parse_list_strings_in_dict

from glchat_sdk import GLChat
from glchat_sdk.evals.config import GLChatConfig, GLChatResponse, HTTPMessageRequest
from glchat_sdk.evals.constant import (
    GLChatDefaults,
    GLChatFieldNames,
    GLChatResponseKeys,
    GLChatSearchTypes,
)
from glchat_sdk.evals.resource_manager import ResourceManager
from glchat_sdk.evals.utils.glchat_utils import (
    create_glchat_client,
    create_message_http,
    create_shared_conversation_http,
    parse_conversation_response,
    parse_sse_string_response,
    resolve_config_from_env,
)

logger = LoggerManager().get_logger(__name__)


async def glchat_inference(
    row: dict[str, Any] | None = None,
    attachments: dict[str, BinaryIO] | None = None,
    config: GLChatConfig | None = None,
    resource_manager: ResourceManager | None = None,
) -> dict[str, Any]:
    """Generate a response from GLChat for dataset evaluation.

    This function coordinates the GLChat inference process by:
    1. Creating a conversation using the GLChat SDK
    2. Sending messages with optional file attachments
    3. Processing and returning the response

    Args:
        row (dict[str, Any] | None): The given data row
        attachments (dict[str, BinaryIO] | None): The given attachments data in a dictionary of
            file names and file contents in binary format
        config (GLChatConfig | None): GLChat configuration
        resource_manager (ResourceManager | None): Resource manager for cleanup

    Returns:
        dict[str, Any]: Dictionary containing generated_response and other fields

    Raises:
        ValueError: If required fields are missing or invalid
        Exception: For other errors during inference
    """
    try:
        if row is None:
            raise ValueError("Row must be provided")

        data_dict = parse_list_strings_in_dict(row)

        if resource_manager is None:
            resource_manager = ResourceManager()

        if config is None:
            raise ValueError("config must be provided")

        # Resolve config values from environment variables if needed and create GLChat client
        config: GLChatConfig = resolve_config_from_env(config)
        glchat_client: GLChat = create_glchat_client(config.base_url, config.api_key)

        # Create shared HTTP session
        shared_http_session = aiohttp.ClientSession()
        resource_manager.set_shared_http_session(shared_http_session)

        # Execute the inference flow
        result = await _execute_inference_flow(
            glchat_client=glchat_client,
            data_dict=data_dict,
            config=config,
            shared_http_session=shared_http_session,
            resource_manager=resource_manager,
            retry_config=get_default_retry_config(),
            attachments=attachments,
        )
        return result

    except asyncio.CancelledError:
        # Handle cancellation gracefully
        raise
    except ValueError as e:
        # Handle validation errors
        return {GLChatResponseKeys.GENERATED_RESPONSE: f"Validation Error: {str(e)}"}
    except aiohttp.ClientError as e:
        # Handle network/HTTP errors
        return {GLChatResponseKeys.GENERATED_RESPONSE: f"Network Error: {str(e)}"}
    except Exception as e:
        # Handle all other errors
        return {GLChatResponseKeys.GENERATED_RESPONSE: f"Error: {str(e)}"}
    finally:
        # Ensure defensive cleanup happens even if errors occur
        if resource_manager:
            await resource_manager.defensive_cleanup()


async def _execute_inference_flow(
    glchat_client: GLChat,
    data_dict: dict[str, Any],
    config: GLChatConfig,
    shared_http_session: aiohttp.ClientSession,
    resource_manager: ResourceManager,
    retry_config: Any,
    attachments: dict[str, BinaryIO] | None = None,
) -> dict[str, Any]:
    """Execute the core inference flow: create conversation and send message.

    Args:
        glchat_client (GLChat): The GLChat client
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        resource_manager (ResourceManager): Resource manager
        retry_config (Any): Retry configuration
        attachments (dict[str, BinaryIO] | None): The given attachments data in a dictionary of
            file names and file contents in binary format

    Returns:
        dict[str, Any]: Result with generated_response and other fields
    """
    # Create conversation
    conversation_id = await _create_conversation(
        glchat_client=glchat_client,
        data_dict=data_dict,
        config=config,
        resource_manager=resource_manager,
        retry_config=retry_config,
    )

    # Send message and get response
    response_data = await _send_message(
        data_dict=data_dict,
        config=config,
        conversation_id=conversation_id,
        shared_http_session=shared_http_session,
        retry_config=retry_config,
        attachments=attachments,
    )

    return response_data


async def _create_conversation(
    glchat_client: GLChat,
    data_dict: dict[str, Any],
    config: GLChatConfig,
    resource_manager: ResourceManager,
    retry_config: Any,
) -> str:
    """Create a GLChat conversation using the SDK.

    Args:
        glchat_client (GLChat): The GLChat client
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration
        resource_manager (ResourceManager): Resource manager
        retry_config (Any): Retry configuration

    Returns:
        str: The conversation ID

    Raises:
        ValueError: If failed to create conversation
    """
    # Use dataset overrides or config defaults
    chatbot_id = data_dict.get(GLChatFieldNames.CHATBOT_ID) or config.chatbot_id
    model_name = data_dict.get(GLChatFieldNames.MODEL_NAME) or config.model_name
    question_id = data_dict.get(GLChatFieldNames.QUESTION_ID, GLChatDefaults.QUESTION_ID)
    username = config.username

    # Create conversation title
    title = f"Evaluation - Question {question_id}"

    try:
        # Apply retry logic to conversation creation
        # Note: asyncio.to_thread automatically handles thread execution
        response = await retry(
            asyncio.to_thread,
            _glchat_conversation_create_sync,
            glchat_client,
            username=username,
            chatbot_id=chatbot_id,
            title=title,
            model_name=model_name,
            retry_config=retry_config,
        )
        conversation_id = parse_conversation_response(response)

        # Track conversation for cleanup
        resource_manager.add_conversation(conversation_id)

        return conversation_id
    except Exception as e:
        raise ValueError(f"Failed to create conversation: {str(e)}") from e


def _glchat_conversation_create_sync(
    glchat_client: GLChat,
    *,
    username: str,
    chatbot_id: str,
    title: str,
    model_name: str | None = None,
) -> dict[str, Any]:
    """Create a GLChat conversation synchronously.

    Args:
        glchat_client (GLChat): The GLChat client
        username (str): The username
        chatbot_id (str): The chatbot ID
        title (str): The conversation title
        model_name (str | None): The model name (optional, will use GLChat default model based on
            chatbot if not provided)

    Returns:
        dict[str, Any]: The API response
    """
    kwargs = {
        GLChatFieldNames.USER_ID: username,
        GLChatFieldNames.CHATBOT_ID: chatbot_id,
        GLChatFieldNames.TITLE: title,
    }
    if model_name is not None:
        kwargs[GLChatFieldNames.MODEL_NAME] = model_name
    return glchat_client.conversation.create(**kwargs)


async def _send_message(
    data_dict: dict[str, Any],
    config: GLChatConfig,
    conversation_id: str,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
    attachments: dict[str, BinaryIO] | None = None,
) -> dict[str, Any]:
    """Send a message to GLChat and process the response.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration
        conversation_id (str): The conversation ID
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        resource_manager (ResourceManager): Resource manager
        retry_config (Any): Retry configuration
        attachments (dict[str, BinaryIO] | None): The given attachments data in a dictionary of
            file names and file contents in binary format

    Returns:
        dict[str, Any]: Response data with generated_response and other fields
    """
    # Check if query is a list for multi-turn support
    query: str | list[str] = data_dict.get(GLChatFieldNames.QUERY, "")
    if isinstance(query, list):
        return await _handle_multi_turn_queries(
            data_dict=data_dict,
            config=config,
            conversation_id=conversation_id,
            shared_http_session=shared_http_session,
            retry_config=retry_config,
            attachments=attachments,
        )

    # Prepare message data for single query
    message_data: dict[str, Any] = _prepare_message_data(data_dict, config)

    try:
        # Download attachments if any
        files: list[BinaryIO] = _handle_attachments(
            data_dict=data_dict,
            attachments=attachments,
        )

        # Send message via HTTP
        response: GLChatResponse = await _send_http_message(
            message_data=message_data,
            files=files,
            conversation_id=conversation_id,
            config=config,
            shared_http_session=shared_http_session,
            retry_config=retry_config,
        )

        # Create shared conversation and get URL
        shared_conv_url: str | None = await _create_shared_conversation_url(
            config=config,
            conversation_id=conversation_id,
            shared_http_session=shared_http_session,
            retry_config=retry_config,
        )

        result = {
            GLChatResponseKeys.GENERATED_RESPONSE: response.final_response,
            GLChatResponseKeys.RETRIEVED_CONTEXT: response.context_data,
        }

        if shared_conv_url:
            result[GLChatResponseKeys.GENERATED_RESPONSE_URL] = shared_conv_url

        return result
    except Exception as e:
        raise ValueError(f"Failed to send message: {str(e)}") from e


def _get_validated_search_type(data_dict: dict[str, Any], config: GLChatConfig) -> str:
    """Get and validate search type from data dict or config.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration

    Returns:
        str: Validated search type

    Raises:
        ValueError: If search type is invalid
    """
    search_type = data_dict.get(GLChatFieldNames.SEARCH_TYPE) or config.search_type
    valid_types = [
        GLChatSearchTypes.NORMAL,
        GLChatSearchTypes.SEARCH,
        GLChatSearchTypes.WEB,
        GLChatSearchTypes.DEEP_RESEARCH,
        GLChatSearchTypes.ESSENTIALS_DEEP_RESEARCH,
        GLChatSearchTypes.COMPREHENSIVE_DEEP_RESEARCH,
    ]

    if search_type not in valid_types:
        raise ValueError(
            f"search_type must be one of: {', '.join(valid_types)}, got: {search_type}"
        )

    return search_type


def _get_validated_pii_setting(data_dict: dict[str, Any], config: GLChatConfig) -> bool:
    """Get and validate PII setting from data dict or config.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration

    Returns:
        bool: Validated PII setting
    """
    enable_pii = data_dict.get(GLChatFieldNames.ENABLE_PII, config.enable_pii)
    if isinstance(enable_pii, str):
        enable_pii_lower = enable_pii.lower()
        if enable_pii_lower in ("true", "1", "yes", "on"):
            data_dict[GLChatFieldNames.ENABLE_PII] = True
            enable_pii = True
        elif enable_pii_lower in ("false", "0", "no", "off"):
            data_dict[GLChatFieldNames.ENABLE_PII] = False
            enable_pii = False
        else:
            logger.warning(f"Unknown PII value '{enable_pii}', keeping as string")

    return bool(enable_pii)


def _determine_connector_based_on_search_type(search_type: str) -> str | None:
    """Determine connector based on search type business rule.

    Business Rule: When search_type is 'search', use 'web' connector. Otherwise, use no connector.

    Args:
        search_type (str): The validated search type

    Returns:
        str | None: Connector to use, or None if no connector needed
    """
    return GLChatDefaults.CONNECTOR_WEB if search_type == GLChatSearchTypes.SEARCH else None


def _prepare_message_data(
    data_dict: dict[str, Any],
    config: GLChatConfig,
) -> dict[str, Any]:
    """Prepare message data from data dictionary and config.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration

    Returns:
        dict[str, Any]: Prepared message data
    """
    search_type = _get_validated_search_type(data_dict, config)
    anonymize_lm = _get_validated_pii_setting(data_dict, config)

    return {
        GLChatFieldNames.CHATBOT_ID: data_dict.get(GLChatFieldNames.CHATBOT_ID)
        or config.chatbot_id,
        GLChatFieldNames.MESSAGE: data_dict.get(GLChatFieldNames.QUERY, ""),
        GLChatFieldNames.MODEL_NAME: data_dict.get(GLChatFieldNames.MODEL_NAME)
        or config.model_name,
        GLChatFieldNames.ANONYMIZE_LM: anonymize_lm,
        GLChatFieldNames.SEARCH_TYPE: search_type,
        GLChatFieldNames.INCLUDE_STATES: config.include_states,
        GLChatFieldNames.CONNECTORS: _determine_connector_based_on_search_type(search_type),
    }


def _handle_attachments(
    data_dict: dict[str, Any],
    attachments: dict[str, BinaryIO] | None = None,
) -> list[BinaryIO]:
    """Handle file attachments based on the data column and the attachments dictionary.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        attachments (dict[str, BinaryIO] | None): The given attachments data in a dictionary of
            file names and file contents in binary format

    Returns:
        list[BinaryIO]: List of file contents

    Raises:
        ValueError: If attachment is not found in the provided attachments.
    """
    attachment_names = data_dict.get(GLChatFieldNames.ATTACHMENTS, [])
    # Check if attachments is None, empty string, "-", or "[]" - treat all as None
    if (
        not attachment_names
        or attachment_names == ""
        or attachment_names == "-"
        or attachment_names == "[]"
        or attachment_names == []
    ):
        return []

    if attachments is None:
        raise ValueError(
            "`attachments` column is available but the attachments dictionary is not provided."
        )

    if isinstance(attachment_names, str):
        attachment_names = [attachment_names]

    files = []
    for attachment_name, attachment_content in attachments.items():
        if attachment_name in attachment_names:
            files.append(attachment_content)
        else:
            raise ValueError(f"Attachment {attachment_name} not found in the provided attachments.")

    return files


async def _send_http_message(
    message_data: dict[str, Any],
    conversation_id: str,
    config: GLChatConfig,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
    files: list[BinaryIO],
    parent_id: str | None = None,
) -> GLChatResponse:
    """Send message via HTTP request to GLChat API.

    Args:
        message_data (dict[str, Any]): The message data dictionary
        conversation_id (str): The conversation ID
        config (GLChatConfig): GLChat configuration
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        retry_config (Any): Retry configuration
        files (list[BinaryIO] | None): List of file contents
        parent_id (str | None): The parent message ID

    Returns:
        GLChatResponse: Response object containing all parsed data
    """
    # Create HTTPMessageRequest from message_data
    request = HTTPMessageRequest(
        chatbot_id=message_data[GLChatFieldNames.CHATBOT_ID],
        message=message_data[GLChatFieldNames.MESSAGE],
        username=config.username,
        conversation_id=conversation_id,
        files=files,
        model_name=message_data[GLChatFieldNames.MODEL_NAME],
        anonymize_lm=message_data[GLChatFieldNames.ANONYMIZE_LM],
        search_type=message_data[GLChatFieldNames.SEARCH_TYPE],
        connectors=message_data[GLChatFieldNames.CONNECTORS],
        include_states=message_data[GLChatFieldNames.INCLUDE_STATES],
        parent_id=parent_id,
    )

    # Apply retry logic to HTTP message sending
    response_text = await retry(
        create_message_http,
        base_url=config.base_url,
        api_key=config.api_key,
        request=request,
        session=shared_http_session,
        retry_config=retry_config,
    )

    # Parse the SSE response using existing pattern
    return parse_sse_string_response(response_text, is_anonymize_lm=request.anonymize_lm)


async def _create_shared_conversation_url(
    config: GLChatConfig,
    conversation_id: str,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
) -> str | None:
    """Create shared conversation and return the URL.

    Args:
        config (GLChatConfig): GLChat configuration
        conversation_id (str): The conversation ID
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        retry_config (Any): Retry configuration

    Returns:
        str | None: The shared conversation URL, or None if creation failed
    """
    try:
        # Apply retry logic to shared conversation creation
        shared_conv_id = await retry(
            create_shared_conversation_http,
            base_url=config.base_url,
            api_key=config.api_key,
            conversation_id=conversation_id,
            username=config.username,
            expiry_days=config.expiry_days,
            session=shared_http_session,
            retry_config=retry_config,
        )

        if not shared_conv_id:
            return None

        # Create the shared conversation URL
        if not config.base_url:
            return None  # Can't create URL without base_url

        base_url_without_api_proxy = config.base_url.replace("/api/proxy/", "/")
        shared_conv_url = f"{base_url_without_api_proxy.rstrip('/')}/c/shared/{shared_conv_id}"

        return shared_conv_url
    except Exception as e:
        logger.warning(f"Failed to create shared conversation: {str(e)}")
        # If shared conversation creation fails, return None (non-critical)
        return None


async def _handle_multi_turn_queries(
    data_dict: dict[str, Any],
    config: GLChatConfig,
    conversation_id: str,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
    attachments: dict[str, BinaryIO] | None = None,
) -> dict[str, Any]:
    """Handle multi-turn queries.

    Args:
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration
        conversation_id (str): The conversation ID
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        resource_manager (ResourceManager): Resource manager
        retry_config (Any): Retry configuration
        attachments (dict[str, BinaryIO] | None): The given attachments data in a dictionary of
            file names and file contents in binary format

    Returns:
        dict[str, Any]: Result with generated_response and other fields
    """
    queries: list[str] = _validate_multi_turn_queries(data_dict)
    files = _handle_attachments(data_dict, attachments)

    # Sequential processing required: each query depends on previous response in conversation
    responses: list[tuple[str, str | None]] = await _process_queries_sequentially(
        queries, data_dict, config, conversation_id, shared_http_session, retry_config, files
    )

    return await _build_multi_turn_result(
        responses, config, conversation_id, shared_http_session, retry_config
    )


def _validate_multi_turn_queries(data_dict: dict[str, Any]) -> list[str]:
    """Validate and extract queries for multi-turn processing.

    Args:
        data_dict (dict[str, Any]): The data dictionary

    Returns:
        list[str]: List of queries
    """
    queries = data_dict.get(GLChatFieldNames.QUERY, [])
    if not isinstance(queries, list) or not queries:
        raise ValueError("query must be a non-empty list for multi-turn support")
    return queries


async def _process_queries_sequentially(
    queries: list[str],
    data_dict: dict[str, Any],
    config: GLChatConfig,
    conversation_id: str,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
    files: list[BinaryIO],
) -> list[tuple[str, str | None]]:
    """Process queries sequentially and return responses.

    Args:
        queries (list[str]): List of queries
        data_dict (dict[str, Any]): The data dictionary
        config (GLChatConfig): GLChat configuration
        conversation_id (str): The conversation ID
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        retry_config (Any): Retry configuration
        files (list[BinaryIO]): List of file objects

    Returns:
        list[tuple[str, str | None]]: List of generated responses and retrieved contexts
    """
    generated_responses = []
    retrieved_contexts = []
    prev_assistant_message_id = None

    for i, query in enumerate(queries):
        query_data_dict = data_dict.copy()
        query_data_dict[GLChatFieldNames.QUERY] = query
        message_data: dict[str, Any] = _prepare_message_data(query_data_dict, config)

        try:
            response: GLChatResponse = await _send_http_message(
                message_data=message_data,
                conversation_id=conversation_id,
                config=config,
                shared_http_session=shared_http_session,
                retry_config=retry_config,
                files=files,
                parent_id=prev_assistant_message_id,
            )
            prev_assistant_message_id = response.assistant_message_id
            generated_responses.append(response.final_response)
            retrieved_contexts.append(response.context_data)
        except Exception as e:
            error_msg = f"Error processing query {i + 1}: {str(e)}"
            generated_responses.append(error_msg)
            retrieved_contexts.append(None)
            logger.warning(error_msg)

    return list(zip(generated_responses, retrieved_contexts, strict=False))


async def _build_multi_turn_result(
    responses: list[tuple[str, str | None]],
    config: GLChatConfig,
    conversation_id: str,
    shared_http_session: aiohttp.ClientSession,
    retry_config: Any,
) -> dict[str, Any]:
    """Build final result for multi-turn queries.

    Args:
        responses (list[tuple[str, str | None]]): List of generated responses and retrieved contexts
        config (GLChatConfig): GLChat configuration
        conversation_id (str): The conversation ID
        shared_http_session (aiohttp.ClientSession): Shared HTTP session
        retry_config (Any): Retry configuration

    Returns:
        dict[str, Any]: Result with generated_response and other fields
    """
    shared_conv_url: str | None = await _create_shared_conversation_url(
        config, conversation_id, shared_http_session, retry_config
    )
    result = {
        GLChatResponseKeys.GENERATED_RESPONSE: responses[-1][0],
        GLChatResponseKeys.RETRIEVED_CONTEXT: responses[-1][1],
    }
    if shared_conv_url:
        result[GLChatResponseKeys.GENERATED_RESPONSE_URL] = shared_conv_url
    return result
