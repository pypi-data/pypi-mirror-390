"""Base classes for AgentBay tools integration."""

import os
from threading import Lock
from typing import Dict, List, Optional

from agentbay import AgentBay, CreateSessionParams, Session
from llama_index.core.tools import BaseTool


class AgentBaySessionManager:
    """
    AgentBay session manager.

    Manages creation, retrieval, and cleanup of AgentBay sessions.
    Supports creating multiple concurrent sessions.

    Args:
        api_key: AgentBay API key. If not provided, reads from AGENTBAY_API_KEY env var.
        default_image_id: Default image ID for sessions. Defaults to "browser_latest".

    Example:
        >>> manager = AgentBaySessionManager()
        >>> # Create multiple concurrent sessions
        >>> sessions = [manager.create() for _ in range(5)]
        >>> # Use sessions...
        >>> manager.cleanup()
    """

    def __init__(
        self, api_key: Optional[str] = None, default_image_id: str = "browser_latest"
    ):
        """Initialize session manager."""
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY is required. "
                "Set it via environment variable or pass as argument."
            )

        self.client = AgentBay(api_key=self.api_key)
        self.default_image_id = default_image_id
        self._sessions: Dict[str, Session] = {}  # session_id -> Session object
        self._lock = Lock()

    def create(
        self,
        image_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> Session:
        """
        Create a new session (always creates new, never reuses).

        Args:
            image_id: Image ID for the session. Uses default if not provided.
            labels: Optional labels for the session.

        Returns:
            Newly created Session object.

        Raises:
            RuntimeError: If session creation fails (e.g., concurrent limit reached).

        Example:
            >>> manager = AgentBaySessionManager()
            >>> # Create 5 independent sessions for concurrent work
            >>> sessions = [manager.create() for _ in range(5)]
        """
        image_id = image_id or self.default_image_id

        with self._lock:
            params = CreateSessionParams(
                image_id=image_id, labels=labels or {"source": "llama-index"}
            )
            result = self.client.create(params)

            if not result.success or result.session is None:
                error_msg = getattr(result, 'error_message', 'Unknown error')

                # Provide helpful hints for common errors
                hint = ""
                if "resource exceed limit" in error_msg.lower() or "exceed" in error_msg.lower():
                    active_count = len(self._sessions)
                    hint = (
                        f"\n\n💡 HINT: Concurrent session limit reached.\n"
                        f"   • Currently active: {active_count} session(s)\n"
                        f"   • Solutions:\n"
                        f"     1. Call cleanup() to release unused sessions\n"
                        f"     2. Reuse existing sessions via get(session_id)\n"
                        f"     3. Contact AgentBay to increase your concurrent limit"
                    )

                raise RuntimeError(f"Failed to create session: {error_msg}{hint}")

            # Store the new session
            session = result.session
            self._sessions[session.session_id] = session

            return session

    def get(self, session_id: str) -> Session:
        """
        Get an existing session by ID.

        Args:
            session_id: Session ID to retrieve.

        Returns:
            Session object.

        Raises:
            RuntimeError: If session not found or expired.

        Example:
            >>> session = manager.create()
            >>> # Later, retrieve by ID
            >>> same_session = manager.get(session.session_id)
        """
        with self._lock:
            # Try local cache first
            if session_id not in self._sessions:
                # Try fetching from server (might be created by another manager)
                result = self.client.get(session_id)
                if result.success and result.session:
                    self._sessions[session_id] = result.session
                    return result.session
                else:
                    raise RuntimeError(
                        f"Session '{session_id}' not found or expired.\n"
                        f"Use create() to create a new session."
                    )

            # Verify session is still alive
            result = self.client.get(session_id)
            if result.success:
                # Update cache
                self._sessions[session_id] = result.session
                return result.session
            else:
                # Session expired, clean up
                del self._sessions[session_id]
                raise RuntimeError(
                    f"Session '{session_id}' has expired.\n"
                    f"Use create() to create a new session."
                )

    def list_sessions(self) -> List[Session]:
        """
        List all currently active sessions managed by this instance.

        Returns:
            List of active Session objects.

        Example:
            >>> sessions = manager.list_sessions()
            >>> print(f"Active sessions: {len(sessions)}")
        """
        with self._lock:
            active_sessions = []
            # Verify each session and clean up expired ones
            for session_id in list(self._sessions.keys()):
                try:
                    session = self.get(session_id)
                    active_sessions.append(session)
                except RuntimeError:
                    # Already cleaned up by get()
                    pass

            return active_sessions

    def cleanup(self, session_id: Optional[str] = None) -> None:
        """
        Clean up sessions.

        Args:
            session_id: If provided, only cleanup this specific session.
                       Otherwise, cleanup all sessions.

        Example:
            >>> # Cleanup specific session
            >>> manager.cleanup(session.session_id)
            >>> # Cleanup all sessions
            >>> manager.cleanup()
        """
        with self._lock:
            if session_id:
                # Cleanup specific session
                if session_id in self._sessions:
                    try:
                        session = self._sessions[session_id]
                        self.client.delete(session)
                    except Exception:
                        pass
                    del self._sessions[session_id]
            else:
                # Cleanup all sessions
                for session in list(self._sessions.values()):
                    try:
                        self.client.delete(session)
                    except Exception:
                        pass
                self._sessions.clear()

    def __del__(self):
        """Cleanup all sessions on deletion."""
        try:
            self.cleanup()
        except Exception:
            pass


class AgentBayBaseTool(BaseTool):
    """
    Base class for AgentBay tools.

    Provides session management and common functionality for all AgentBay tools.

    Args:
        session_manager: Optional session manager. Creates new one if not provided.
        session: Optional specific session to use. If provided, this session will be used
                directly instead of creating/getting from session_manager.
        image_id: Image ID for the session (only used if session is not provided).
        **kwargs: Additional arguments passed to BaseTool.

    Example:
        >>> # Option 1: Let tool create session automatically
        >>> class MyTool(AgentBayBaseTool):
        ...     def _run(self, query: str) -> str:
        ...         session = self._get_session()
        ...         # Use session...
        ...         return result
        >>>
        >>> # Option 2: Provide specific session
        >>> manager = AgentBaySessionManager()
        >>> session = manager.create()
        >>> tool = MyTool(session=session)
    """

    def __init__(
        self,
        session_manager: Optional[AgentBaySessionManager] = None,
        session: Optional[Session] = None,
        image_id: str = "browser_latest",
        **kwargs,
    ):
        """Initialize base tool."""
        super().__init__(**kwargs)
        self.session_manager = session_manager or AgentBaySessionManager()
        self._session = session  # Specific session to use
        self._session_id: Optional[str] = None  # Cached session ID
        self.image_id = image_id

    def _get_session(self) -> Session:
        """
        Get the session for this tool.

        If a specific session was provided during initialization, use that.
        Otherwise, create a new session or reuse cached one.

        Returns:
            Session object.
        """
        # If specific session was provided, use it
        if self._session is not None:
            return self._session

        # If we have a cached session_id, try to get it
        if self._session_id:
            try:
                return self.session_manager.get(self._session_id)
            except RuntimeError:
                # Session expired, create new one
                self._session_id = None

        # Create new session and cache it
        session = self.session_manager.create(self.image_id)
        self._session_id = session.session_id
        return session

