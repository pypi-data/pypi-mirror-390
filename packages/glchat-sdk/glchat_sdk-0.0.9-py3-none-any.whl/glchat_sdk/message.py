"""Response handling for the GLChat Python client.

This module provides the MessageAPI class for handling message operations
with the GLChat backend, including streaming responses and file uploads.

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, BinaryIO, TypeVar
from urllib.parse import urljoin

import httpx

from glchat_sdk.models import MessageRequest, MessageResponse

logger = logging.getLogger(__name__)

# Type variable for file types
FileType = TypeVar("FileType", str, Path, BinaryIO, bytes)

FILE_TYPE = "application/octet-stream"
DATA_PREFIX = "data:"


class MessageAPI:
    """Handles message API operations for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_inputs(self, chatbot_id: str, message: str) -> None:
        """Validate input parameters.

        Args:
            chatbot_id (str): Chatbot identifier
            message (str): User message

        Raises:
            ValueError: If chatbot_id or message is empty
        """
        if not chatbot_id:
            raise ValueError("chatbot_id cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")

    def _prepare_request_data(
        self,
        chatbot_id: str,
        message: str,
        parent_id: str | None = None,
        source: str | None = None,
        quote: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        user_message_id: str | None = None,
        assistant_message_id: str | None = None,
        chat_history: str | None = None,
        stream_id: str | None = None,
        metadata: str | None = None,
        model_name: str | None = None,
        anonymize_em: bool | None = None,
        anonymize_lm: bool | None = None,
        use_cache: bool | None = None,
        search_type: str | None = None,
        agent_ids: list[str] | None = None,
        exclude_events: list[str] | None = None,
        stream_message_only: bool | None = None,
        exclude_prefix: bool | None = None,
        include_states: bool | None = None,
        filters: str | None = None,
    ) -> dict[str, Any]:
        """Prepare request data for the API call.

        Args:
            chatbot_id (str): Required chatbot identifier
            message (str): Required user message
            parent_id (str | None): Parent message ID for threading
            source (str | None): Source identifier for the message
            quote (str | None): Quoted message content
            user_id (str | None): User identifier
            conversation_id (str | None): Conversation identifier
            user_message_id (str | None): User message identifier
            assistant_message_id (str | None): Assistant message identifier
            chat_history (str | None): Chat history context
            stream_id (str | None): Stream identifier
            metadata (str | None): Additional metadata
            model_name (str | None): Model name to use for generation
            anonymize_em (bool | None): Whether to anonymize embeddings
            anonymize_lm (bool | None): Whether to anonymize language model
            use_cache (bool | None): Whether to use cached responses
            search_type (str | None): Type of search to perform
            agent_ids (list[str] | None): List of agent IDs to involve
            exclude_events (list[str] | None): List of events to exclude
            stream_message_only (bool | None): Whether to stream message only
            exclude_prefix (bool | None): Whether to exclude prefix
            include_states (bool | None): Whether to include states
            filters (str | None): Filters to apply to the message request

        Returns:
            dict[str, Any]: Dictionary containing the prepared request data
        """
        request = MessageRequest(
            chatbot_id=chatbot_id,
            message=message,
            parent_id=parent_id,
            source=source,
            quote=quote,
            user_id=user_id,
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            chat_history=chat_history,
            stream_id=stream_id,
            metadata=metadata,
            model_name=model_name,
            anonymize_em=anonymize_em,
            anonymize_lm=anonymize_lm,
            use_cache=use_cache,
            search_type=search_type,
            agent_ids=agent_ids,
            exclude_events=exclude_events,
            stream_message_only=stream_message_only,
            exclude_prefix=exclude_prefix,
            include_states=include_states,
            filters=filters,
        )
        return request.model_dump(exclude_none=True)

    def _prepare_headers(
        self, extra_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        """Prepare headers for the API request.

        Args:
            extra_headers (dict[str, str] | None): Additional headers to merge with default headers

        Returns:
            dict[str, str]: Dictionary containing the request headers
        """
        # Start with default headers from client
        headers = self._client.default_headers.copy()

        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"

        # Merge with extra headers if provided
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _process_file_item(
        self, file_item: FileType
    ) -> tuple[str, tuple[str, FileType, str]]:
        """Process a single file item and return the file tuple for httpx.

        Args:
            file_item (FileType): Item to process

        Returns:
            tuple[str, tuple[str, FileType, str]]: Tuple of
                (field_name, (filename, file_content, content_type))

        Raises:
            ValueError: If file type is not supported
        """
        if isinstance(file_item, str | Path):
            # File path
            file_path = Path(file_item)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, "rb") as f:
                return ("files", (file_path.name, f.read(), FILE_TYPE))
        elif isinstance(file_item, bytes):
            # Raw bytes
            return ("files", ("file", file_item, FILE_TYPE))
        elif hasattr(file_item, "read"):
            # File-like object - pass directly to avoid memory issues
            filename = getattr(file_item, "name", "file")
            return ("files", (filename, file_item, FILE_TYPE))
        else:
            raise ValueError(f"Unsupported file type: {type(file_item)}")

    def _prepare_files(
        self, files: list[FileType] | None
    ) -> list[tuple[str, tuple[str, FileType, str]]] | None:
        """Prepare files for upload.

        Args:
            files (list[FileType] | None): List of files to process

        Returns:
            list[tuple[str, tuple[str, FileType, str]]] | None: List of file tuples for httpx
                or None if no files

        Raises:
            ValueError: If any file type is not supported
            FileNotFoundError: If any file path doesn't exist
        """
        if not files:
            return None

        files_data = []
        for file_item in files:
            try:
                file_tuple = self._process_file_item(file_item)
                files_data.append(file_tuple)
            except (ValueError, FileNotFoundError) as e:
                logger.error("Error processing file %s: %s", file_item, str(e))
                raise

        return files_data

    def _make_streaming_request(
        self,
        url: str,
        data: dict[str, Any],
        files: list[tuple[str, tuple[str, FileType, str]]] | None,
        headers: dict[str, str],
    ) -> Iterator[bytes]:
        """Make the streaming HTTP request.

        Args:
            url (str): API endpoint URL
            data (dict[str, Any]): Request data
            files (list[tuple[str, tuple[str, FileType, str]]] | None): Prepared files data
            headers (dict[str, str]): Request headers

        Yields:
            bytes: Streaming response chunks

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        timeout = httpx.Timeout(self._client.timeout, read=self._client.timeout)

        with httpx.Client(timeout=timeout) as client:
            with client.stream(
                "POST",
                url,
                data=data,
                files=files,
                headers=headers,
            ) as response:
                response.raise_for_status()
                yield from response.iter_bytes()

    def _create_streaming(
        self,
        url: str,
        data: dict[str, Any],
        files: list[tuple[str, tuple[str, FileType, str]]] | None,
        headers: dict[str, str],
    ) -> Iterator[bytes]:
        """Internal method for streaming response.

        Args:
            url (str): API endpoint URL
            data (dict[str, Any]): Request data
            files (list[tuple[str, tuple[str, FileType, str]]] | None): Prepared files data
            headers (dict[str, str]): Request headers

        Yields:
            bytes: Streaming response chunks
        """
        yield from self._make_streaming_request(url, data, files, headers)

    def _create_non_streaming(
        self,
        url: str,
        data: dict[str, Any],
        files: list[tuple[str, tuple[str, FileType, str]]] | None,
        headers: dict[str, str],
    ) -> MessageResponse:
        """Internal method for non-streaming response.

        Check if the chunk can be considered as last chunk (status == response)
        because actual last chunk might be just reference

        Args:
            url (str): API endpoint URL
            data (dict[str, Any]): Request data
            files (list[tuple[str, tuple[str, FileType, str]]] | None): Prepared files data
            headers (dict[str, str]): Request headers

        Returns:
            MessageResponse: The last response chunk
        """
        last_chunk = MessageResponse()
        for chunk in self._make_streaming_request(url, data, files, headers):
            temp = chunk.decode("utf-8")
            json_str = temp.removeprefix(DATA_PREFIX).strip()
            try:
                parsed = json.loads(json_str)

                # Check if it contains "status" with value "response"
                if isinstance(parsed, dict) and parsed.get("status") == "response":
                    last_chunk = MessageResponse(
                        status=parsed.get("status"),
                        message=parsed.get("message"),
                        original=parsed
                    )
            except json.JSONDecodeError:
                # If JSON parsing fails, keep the original last_chunk
                pass

        return last_chunk

    def create(
        self,
        message: str,
        application_id: str | None = None,
        chatbot_id: str | None = None,
        files: list[FileType] | None = None,
        parent_id: str | None = None,
        source: str | None = None,
        quote: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        user_message_id: str | None = None,
        assistant_message_id: str | None = None,
        chat_history: str | None = None,
        stream_id: str | None = None,
        metadata: str | None = None,
        model_name: str | None = None,
        anonymize_em: bool | None = None,
        anonymize_lm: bool | None = None,
        use_cache: bool | None = None,
        search_type: str | None = None,
        agent_id: str | None = None,
        exclude_events: list[str] | None = None,
        stream_message_only: bool | None = None,
        exclude_prefix: bool | None = None,
        include_states: bool | None = None,
        filters: str | None = None,
        stream: bool | None = None,
        extra_headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Iterator[bytes] | MessageResponse:
        """
        Create a streaming response from the GLChat API.

        Args:
            application_id (str | None): Application identifier
            chatbot_id (str | None): Use application_id instead
            message (str): Required user message
            files (list[FileType] | None): List of files
                (filepath, binary, file object, or bytes)
            parent_id (str | None): Parent message ID for threading
            source (str | None): Source identifier for the message
            quote (str | None): Quoted message content
            user_id (str | None): User identifier
            conversation_id (str | None): Conversation identifier
            user_message_id (str | None): User message identifier
            assistant_message_id (str | None): Assistant message identifier
            chat_history (str | None): Chat history context
            stream_id (str | None): Stream identifier
            metadata (str | None): Additional metadata
            model_name (str | None): Model name to use for generation
            anonymize_em (bool | None): Whether to anonymize embeddings
            anonymize_lm (bool | None): Whether to anonymize language model
            use_cache (bool | None): Whether to use cached responses
            search_type (str | None): Type of search to perform
            agent_id (str | None): Agent ID to involve
            exclude_events (list[str] | None): List of events to exclude
            stream_message_only (bool | None): Whether to stream message only
            exclude_prefix (bool | None): Whether to exclude prefix
            include_states (bool | None): Whether to include states
            filters (str | None): Filters to apply to the message request
            stream (bool | None): If True or None, yields streaming response chunks.
                If False, returns only the last chunk with status "response"
                or empty MessageResponse if no such chunk found.
            extra_headers (dict[str, str] | None): Additional headers to include in the request
            **kwargs: Additional arbitrary parameters to include in the request payload

        Yields:
            bytes: Streaming response chunks (when stream=True)

        Returns:
            MessageResponse: The last response chunk (when stream=False)

        Raises:
            ValueError: If input validation fails or if both chatbot_id and
                application_id are provided
            FileNotFoundError: If any file path doesn't exist
            httpx.HTTPStatusError: If the API request fails
        """
        # Validate that exactly one of chatbot_id or application_id is provided
        if chatbot_id and application_id:
            raise ValueError("Cannot provide both application_id and chatbot_id")
        if not chatbot_id and not application_id:
            raise ValueError("Must provide either application_id or chatbot_id")

        # Use chatbot_id for backward compatibility (application_id is treated as chatbot_id)
        actual_chatbot_id = chatbot_id or application_id
        agent_ids = [agent_id] if agent_id else None

        # Validate inputs
        self._validate_inputs(actual_chatbot_id, message)

        logger.debug("Sending message to chatbot %s", actual_chatbot_id)

        # Prepare request components
        url = urljoin(self._client.base_url, "message")
        data = self._prepare_request_data(
            chatbot_id=actual_chatbot_id,
            message=message,
            parent_id=parent_id,
            source=source,
            quote=quote,
            user_id=user_id,
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            chat_history=chat_history,
            stream_id=stream_id,
            metadata=metadata,
            model_name=model_name,
            anonymize_em=anonymize_em,
            anonymize_lm=anonymize_lm,
            agent_ids=agent_ids,
            use_cache=use_cache,
            search_type=search_type,
            exclude_events=exclude_events,
            stream_message_only=stream_message_only,
            exclude_prefix=exclude_prefix,
            include_states=include_states,
            filters=filters,
        )

        # Merge any additional kwargs into the data payload
        if kwargs:
            data.update(kwargs)

        base_headers = self._prepare_headers()
        if extra_headers:
            base_headers.update(extra_headers)
        files_data = self._prepare_files(files)

        # Make the streaming request
        if stream is None or stream:
            # Return streaming iterator
            return self._create_streaming(url, data, files_data, base_headers)

        # Return the last chunk with status "response"
        # or empty MessageResponse if no such chunk found.
        return self._create_non_streaming(url, data, files_data, base_headers)
