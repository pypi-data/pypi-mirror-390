"""Command execution tools for AgentBay."""

from typing import Optional

from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_command_execute_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create command execution tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for executing commands.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    # Cache session_id to reuse session across multiple calls
    cached_session_id = [None]

    def execute_command(command: str) -> str:
        """
        Execute a shell command in the AgentBay session.

        Args:
            command: Command to execute.

        Returns:
            Command output.
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
            result = session.command.execute_command(command, timeout_ms=30000)

            if not result.success:
                return f"Command failed: {result.error_message}"

            return f"Command executed successfully:\n{result.output}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=execute_command,
        name="command_execute",
        description=(
            "Execute a shell command in the AgentBay session. "
            "Input should be the command to execute. "
            "Example: 'ls -la' or 'python script.py' or 'npm install'"
        ),
    )


def create_python_execute_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create Python code execution tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for executing Python code.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    # Cache session_id to reuse session across multiple calls
    cached_session_id = [None]

    def execute_python(code: str) -> str:
        """
        Execute Python code in the AgentBay session.

        Args:
            code: Python code to execute.

        Returns:
            Execution result.
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

            temp_file = "/tmp/temp_script.py"
            write_result = session.file_system.write_file(
                temp_file, code, "overwrite"
            )

            if not write_result.success:
                return f"Failed to write code: {write_result.error_message}"

            # Use python3 for compatibility with browser_latest image
            exec_result = session.command.execute_command(f"python3 {temp_file}", timeout_ms=30000)

            if not exec_result.success:
                return f"Execution failed: {exec_result.error_message}"

            return f"Python code executed successfully:\n{exec_result.output}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=execute_python,
        name="python_execute",
        description=(
            "Execute Python code in the AgentBay session. "
            "Input should be valid Python code. "
            'Example: \'print("Hello")\' or \'import json; print(json.dumps({"a": 1}))\''
        ),
    )
