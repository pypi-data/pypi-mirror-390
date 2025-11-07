"""AgentBay tools integration for LlamaIndex."""

from typing import Optional

from .base import AgentBaySessionManager, AgentBayBaseTool
from .browser_tools import (
    create_browser_screenshot_tool,
    create_browser_info_tool,
    create_browser_navigate_tool,
    create_browser_get_content_tool,
)
from .code_tools import (
    create_python_run_tool,
    create_javascript_run_tool,
    create_code_tools,
)
from .command_tools import create_command_execute_tool, create_python_execute_tool
from .filesystem_tools import (
    create_file_list_tool,
    create_file_read_tool,
    create_file_write_tool,
    create_file_download_tool,
)
from .rag_helper import (
    AgentBayRAGManager,
    InsightExtractor,
    create_rag_manager,
)

__all__ = [
    "AgentBaySessionManager",
    "AgentBayBaseTool",
    "AgentBayRAGManager",
    "InsightExtractor",
    "create_browser_screenshot_tool",
    "create_browser_info_tool",
    "create_browser_navigate_tool",
    "create_browser_get_content_tool",
    "create_file_read_tool",
    "create_file_write_tool",
    "create_file_list_tool",
    "create_file_download_tool",
    "create_command_execute_tool",
    "create_python_execute_tool",
    "create_python_run_tool",
    "create_javascript_run_tool",
    "create_rag_manager",
    "create_browser_tools",
    "create_filesystem_tools",
    "create_command_tools",
    "create_code_tools",
    "create_all_tools",
    "create_browser_agent_tools",  # Recommended: single-image tool set
    "create_code_agent_tools",     # Recommended: single-image tool set
]


def create_browser_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> list:
    """
    Create all browser tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        List of browser tools.

    Example:
        >>> from llama_index.tools.agentbay import create_browser_tools
        >>> tools = create_browser_tools()

    Note:
        Browser tools provide navigation, content retrieval, screenshot, and CDP endpoint info.
        For advanced browser automation (clicking, form filling, etc.),
        use Playwright directly with the browser endpoint from browser_info tool.
    """
    return [
        create_browser_navigate_tool(session_manager, image_id),
        create_browser_get_content_tool(session_manager, image_id),
        # Note: screenshot tool removed - use navigate + get_content for text-based extraction
        create_browser_info_tool(session_manager, image_id),
    ]


def create_filesystem_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> list:
    """
    Create all filesystem tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        List of filesystem tools.

    Example:
        >>> from llama_index.tools.agentbay import create_filesystem_tools
        >>> tools = create_filesystem_tools()
    """
    return [
        create_file_read_tool(session_manager, image_id),
        create_file_write_tool(session_manager, image_id),
        create_file_list_tool(session_manager, image_id),
        create_file_download_tool(session_manager, image_id),
    ]


def create_command_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> list:
    """
    Create all command execution tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        List of command execution tools.

    Example:
        >>> from llama_index.tools.agentbay import create_command_tools
        >>> tools = create_command_tools()
    """
    return [
        create_command_execute_tool(session_manager, image_id),
        create_python_execute_tool(session_manager, image_id),
    ]


def create_all_tools(
    api_key: Optional[str] = None,
    browser_enabled: bool = True,
    filesystem_enabled: bool = True,
    command_enabled: bool = True,
    code_enabled: bool = True,
) -> list:
    """
    Create all AgentBay tools.

    ⚠️ WARNING: This will create tools using MULTIPLE image types:
    - browser_latest (browser tools)
    - code_latest (code execution, filesystem, commands)

    This creates MULTIPLE AgentBay sessions which may:
    1. Exceed your API key's concurrent session limit
    2. Prevent file sharing between browser and code tools

    RECOMMENDED: Use create_browser_agent_tools() or create_code_agent_tools() instead
    for single-image tool sets.

    Args:
        api_key: AgentBay API key. If not provided, reads from AGENTBAY_API_KEY env var.
        browser_enabled: Whether to enable browser tools. Defaults to True.
        filesystem_enabled: Whether to enable filesystem tools. Defaults to True.
        command_enabled: Whether to enable command execution tools. Defaults to True.
        code_enabled: Whether to enable code execution tools (run_code). Defaults to True.

    Returns:
        List of all enabled tools.

    Example:
        >>> from llama_index.tools.agentbay import create_all_tools
        >>> tools = create_all_tools()
    """
    session_manager = AgentBaySessionManager(api_key=api_key)

    tools = []

    if browser_enabled:
        tools.extend(create_browser_tools(session_manager))

    if filesystem_enabled:
        tools.extend(create_filesystem_tools(session_manager))

    if command_enabled:
        tools.extend(create_command_tools(session_manager))

    if code_enabled:
        tools.extend(create_code_tools(session_manager))

    return tools


def create_browser_agent_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
) -> list:
    """
    Create a complete tool set for browser automation agents.

    All tools use browser_latest image, sharing a single AgentBay session.

    Included capabilities:
    - Browser: screenshot, endpoint info (for Playwright)
    - File system: read, write, list, download
    - Commands: execute shell commands

    Note: For code execution WITH browser, use Playwright in the browser environment
    (not session.code.run_code which requires code_latest image).

    Args:
        session_manager: Optional session manager. If not provided, creates a new one
                        with browser_latest as default image.

    Returns:
        List of tools using browser_latest image.

    Example:
        >>> from llama_index.tools.agentbay import create_browser_agent_tools
        >>> from llama_index.core.agent import ReActAgent
        >>>
        >>> tools = create_browser_agent_tools()
        >>> agent = ReActAgent.from_tools(tools, llm=llm)
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager(default_image_id="browser_latest")

    return [
        *create_browser_tools(session_manager, "browser_latest"),
        *create_filesystem_tools(session_manager, "browser_latest"),
        *create_command_tools(session_manager, "browser_latest"),
    ]


def create_code_agent_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
) -> list:
    """
    Create a complete tool set for code execution agents.

    All tools use code_latest image, sharing a single AgentBay session.

    Included capabilities:
    - Code execution: Python, JavaScript via run_code()
    - File system: read, write, list, download
    - Commands: execute shell commands

    Note: code_latest does NOT include browser capabilities. For browser automation,
    use create_browser_agent_tools() instead.

    Args:
        session_manager: Optional session manager. If not provided, creates a new one
                        with code_latest as default image.

    Returns:
        List of tools using code_latest image.

    Example:
        >>> from llama_index.tools.agentbay import create_code_agent_tools
        >>> from llama_index.core.agent import ReActAgent
        >>>
        >>> tools = create_code_agent_tools()
        >>> agent = ReActAgent.from_tools(tools, llm=llm)
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager(default_image_id="code_latest")

    return [
        *create_code_tools(session_manager, "code_latest"),
        *create_filesystem_tools(session_manager, "code_latest"),
        *create_command_tools(session_manager, "code_latest"),
    ]
