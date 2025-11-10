"""Resource management module for GLChat evaluation.

This module provides resource tracking and cleanup functionality for GLChat evaluation,
ensuring proper cleanup of conversations, temporary files, and HTTP sessions.

Code Quality Requirement: All functions must enforce maximum 5 lines when possible,
creating separate helper files if functions cannot be broken down further.

Authors:
    Christina Alexandra (christina.alexandra@gdplabs.id)

References:
    NONE
"""

import aiohttp

TEMP_FILE_CLEANUP_TIMEOUT_SECONDS = 30.0


class ResourceManager:
    """Manages temporary resources and cleanup operations for GLChat evaluation.

    This class tracks various types of resources that need cleanup after evaluation,
    including conversations, temporary files, and a shared HTTP session.

    Attributes:
        conversations (list[str]): List of conversation IDs to cleanup
        temp_files (list[tempfile.TemporaryDirectory]): List of temporary directories
        shared_http_session (aiohttp.ClientSession | None): Shared HTTP session to close
    """

    def __init__(self) -> None:
        """Initialize the ResourceManager with empty resource lists."""
        self.conversations: list[str] = []
        self.shared_http_session: aiohttp.ClientSession | None = None

    def add_conversation(self, conversation_id: str) -> None:
        """Add a conversation ID to the cleanup list.

        Args:
            conversation_id (str): The conversation ID to track for cleanup
        """
        self.conversations.append(conversation_id)

    def set_shared_http_session(self, session: aiohttp.ClientSession) -> None:
        """Set the shared HTTP session for cleanup.

        Args:
            session (aiohttp.ClientSession): The shared HTTP session to track for cleanup
        """
        self.shared_http_session = session

    async def cleanup_all(self) -> None:
        """Clean up all tracked resources."""
        await self.cleanup_conversations()
        await self.cleanup_http_session()

    async def cleanup_conversations(self) -> None:
        """Clear the local list of tracked conversation IDs.

        Note:
            This only clears the in-memory tracking list. Conversations remain
            on the GLChat server for inspection, audit, or debugging purposes.
            Server-side deletion is intentionally not performed.
        """
        if not self.conversations:
            return

        self.conversations.clear()

    async def cleanup_http_session(self) -> None:
        """Clean up the shared HTTP session."""
        if self.shared_http_session and not self.shared_http_session.closed:
            try:
                await self.shared_http_session.close()
            except Exception:
                pass  # Ignore cleanup errors
        self.shared_http_session = None

    async def defensive_cleanup(self) -> None:
        """Perform defensive cleanup that ignores all errors."""
        try:
            await self.cleanup_all()
        except Exception:
            # Ignore all cleanup errors to ensure we don't mask the original error
            pass
