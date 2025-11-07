"""Browser automation tools for AgentBay.

Note: Browser tools use AgentBay's browser_latest image and Playwright CDP protocol.
For complex browser automation, consider using Playwright directly with AgentBay browser endpoint.
"""

from typing import Optional

from agentbay.browser import BrowserOption
from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_browser_screenshot_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser screenshot tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for taking screenshots.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    # Cache session_id to reuse session across multiple calls
    cached_session_id = [None]

    def take_screenshot() -> str:
        """
        Take a screenshot of the current browser page.

        Returns:
            Screenshot data URL or error message.
        """
        try:
            # Try to reuse cached session, otherwise create new one
            if cached_session_id[0]:
                try:
                    session = session_manager.get(cached_session_id[0])
                except RuntimeError:
                    session = session_manager.create(image_id)
                    cached_session_id[0] = session.session_id
            else:
                session = session_manager.create(image_id)
                cached_session_id[0] = session.session_id

            # Initialize browser if needed
            if not hasattr(session, "_browser_initialized"):
                browser_option = BrowserOption()
                success = session.browser.initialize(browser_option)
                if not success:
                    return "Failed to initialize browser"
                session._browser_initialized = True

            # Take screenshot using browser agent
            result = session.browser.agent.screenshot(full_page=True)

            if result.startswith("data:image"):
                return f"Screenshot captured successfully: {result[:100]}..."
            else:
                return f"Screenshot failed: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=take_screenshot,
        name="browser_screenshot",
        description=(
            "Take a screenshot of the current browser page. "
            "Returns a base64 encoded data URL of the screenshot. "
            "Note: Browser must be initialized first."
        ),
    )


def create_browser_navigate_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser navigate tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for navigating to URLs.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def navigate_to_url(url: str) -> str:
        """
        Navigate browser to a URL.

        Args:
            url: The URL to navigate to (e.g., 'https://www.example.com')

        Returns:
            Success message or error.
        """
        try:
            # Get or create shared session for this image_id
            cache_key = f"_browser_session_{image_id}"
            if hasattr(session_manager, cache_key):
                try:
                    session = session_manager.get(getattr(session_manager, cache_key))
                except RuntimeError:
                    session = session_manager.create(image_id)
                    setattr(session_manager, cache_key, session.session_id)
            else:
                session = session_manager.create(image_id)
                setattr(session_manager, cache_key, session.session_id)

            # Initialize browser if needed
            if not hasattr(session, "_browser_initialized"):
                browser_option = BrowserOption()
                success = session.browser.initialize(browser_option)
                if not success:
                    return "Failed to initialize browser"
                session._browser_initialized = True

                # Get CDP endpoint and connect with Playwright (sync API)
                from playwright.sync_api import sync_playwright

                endpoint_url = session.browser.get_endpoint_url()
                playwright = sync_playwright().start()
                browser = playwright.chromium.connect_over_cdp(endpoint_url)
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                else:
                    context = browser.new_context()

                pages = context.pages
                if pages:
                    page = pages[0]
                else:
                    page = context.new_page()

                # Cache Playwright objects on session_manager instead of session instance
                # so they can be shared across tool calls
                pw_cache_key = f"_pw_{cache_key}"
                setattr(session_manager, pw_cache_key, {
                    'playwright': playwright,
                    'browser': browser,
                    'context': context,
                    'page': page
                })

            # Get page from cache
            pw_cache_key = f"_pw_{cache_key}"
            page = getattr(session_manager, pw_cache_key)['page']

            # Navigate to URL using Playwright
            page.goto(url, timeout=30000)

            return f"Successfully navigated to {url}. You can now use browser_screenshot or browser_get_content to view the page."

        except Exception as e:
            return f"Error navigating to {url}: {str(e)}"

    return FunctionTool.from_defaults(
        fn=navigate_to_url,
        name="browser_navigate",
        description=(
            "Navigate the browser to a specific URL. "
            "Input should be a valid URL (e.g., 'https://www.example.com'). "
            "After navigation, you can use browser_screenshot or browser_get_content to view the page."
        ),
    )


def create_browser_get_content_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser get content tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for getting page content.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def get_page_content() -> str:
        """
        Get the HTML content of the current browser page.

        Returns:
            Page HTML content or error message.
        """
        try:
            # Get or create shared session for this image_id (same as navigate tool)
            cache_key = f"_browser_session_{image_id}"
            if hasattr(session_manager, cache_key):
                try:
                    session = session_manager.get(getattr(session_manager, cache_key))
                except RuntimeError:
                    session = session_manager.create(image_id)
                    setattr(session_manager, cache_key, session.session_id)
            else:
                session = session_manager.create(image_id)
                setattr(session_manager, cache_key, session.session_id)

            # Check if Playwright page is initialized
            pw_cache_key = f"_pw_{cache_key}"
            if not hasattr(session_manager, pw_cache_key):
                return "Browser not initialized. Please use browser_navigate first to visit a URL."

            # Get page from cache and retrieve content
            page = getattr(session_manager, pw_cache_key)['page']
            content = page.content()

            # Limit content length to avoid overwhelming the LLM
            if len(content) > 10000:
                content = content[:10000] + "\n\n... (content truncated, total length: " + str(len(content)) + " characters)"

            return content

        except Exception as e:
            return f"Error getting page content: {str(e)}"

    return FunctionTool.from_defaults(
        fn=get_page_content,
        name="browser_get_content",
        description=(
            "Get the HTML content of the current browser page. "
            "Returns the full HTML source of the page. "
            "Note: You must navigate to a URL first using browser_navigate."
        ),
    )


def create_browser_info_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser info tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for getting browser information.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    # Cache session_id to reuse session across multiple calls
    cached_session_id = [None]

    def get_browser_info() -> str:
        """
        Get browser endpoint information.

        Returns:
            Browser endpoint URL and status.
        """
        try:
            # Try to reuse cached session, otherwise create new one
            if cached_session_id[0]:
                try:
                    session = session_manager.get(cached_session_id[0])
                except RuntimeError:
                    session = session_manager.create(image_id)
                    cached_session_id[0] = session.session_id
            else:
                session = session_manager.create(image_id)
                cached_session_id[0] = session.session_id

            # Initialize browser if needed
            if not hasattr(session, "_browser_initialized"):
                browser_option = BrowserOption()
                success = session.browser.initialize(browser_option)
                if not success:
                    return "Failed to initialize browser"
                session._browser_initialized = True

            # Get browser endpoint
            endpoint_url = session.browser.get_endpoint_url()

            return (
                f"Browser initialized successfully.\n"
                f"CDP Endpoint: {endpoint_url}\n"
                f"You can connect to this browser using Playwright:\n"
                f"  browser = await playwright.chromium.connect_over_cdp('{endpoint_url}')"
            )

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=get_browser_info,
        name="browser_info",
        description=(
            "Get browser endpoint information for Playwright connection. "
            "Returns the CDP endpoint URL that can be used to connect "
            "with Playwright for advanced browser automation."
        ),
    )
