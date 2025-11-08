from typing import Any
from uuid import uuid4

import pytest
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat

from universal_mcp.agents import get_agent
from universal_mcp.agents.utils import get_message_text


class MockToolRegistry(ToolRegistry):
    """Mock implementation of ToolRegistry with an interface compatible with AgentrRegistry."""

    def __init__(self, **kwargs: Any):
        """Initialize the MockToolRegistry."""
        self._apps = [
            {
                "id": "google_mail",
                "name": "google_mail",
                "description": "Send and manage emails.",
            },
            {
                "id": "slack",
                "name": "slack",
                "description": "Team communication and messaging.",
            },
            {
                "id": "google_calendar",
                "name": "google_calendar",
                "description": "Schedule and manage calendar events.",
            },
            {
                "id": "jira",
                "name": "jira",
                "description": "Project tracking and issue management.",
            },
            {
                "id": "github",
                "name": "github",
                "description": "Code hosting, version control, and collaboration.",
            },
        ]
        self._connected_apps = ["google_mail", "google_calendar", "github"]
        self._tools = {
            "google_mail": [
                {
                    "id": "send_email",
                    "name": "send_email",
                    "description": "Send an email to a recipient.",
                },
                {
                    "id": "read_email",
                    "name": "read_email",
                    "description": "Read emails from inbox.",
                },
                {
                    "id": "create_draft",
                    "name": "create_draft",
                    "description": "Create a draft email.",
                },
            ],
            "slack": [
                {
                    "id": "send_message",
                    "name": "send_message",
                    "description": "Send a message to a team channel.",
                },
                {
                    "id": "read_channel",
                    "name": "read_channel",
                    "description": "Read messages from a channel.",
                },
            ],
            "google_calendar": [
                {
                    "id": "create_event",
                    "name": "create_event",
                    "description": "Create a new calendar event.",
                },
                {
                    "id": "find_event",
                    "name": "find_event",
                    "description": "Find an event in the calendar.",
                },
            ],
            "github": [
                {
                    "id": "create_issue",
                    "name": "create_issue",
                    "description": "Create an issue in a repository.",
                },
                {
                    "id": "get_issue",
                    "name": "get_issue",
                    "description": "Get details of a specific issue.",
                },
                {
                    "id": "create_pull_request",
                    "name": "create_pull_request",
                    "description": "Create a pull request.",
                },
                {
                    "id": "get_repository",
                    "name": "get_repository",
                    "description": "Get details of a repository.",
                },
            ],
        }
        self._tool_mappings = {
            "google_mail": {
                "email": ["send_email", "read_email", "create_draft"],
                "send": ["send_email"],
            },
            "slack": {
                "message": ["send_message", "read_channel"],
                "team": ["send_message"],
            },
            "google_calendar": {
                "meeting": ["create_event", "find_event"],
                "schedule": ["create_event"],
            },
            "github": {
                "issue": ["create_issue", "get_issue"],
                "code": ["create_pull_request", "get_repository"],
            },
        }
        super().__init__(**kwargs)

    def _load_tools_from_app(self, app_id: str, tools: list[str]) -> None:
        """Mock implementation for loading tools."""
        pass

    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Get list of available apps."""
        return self._apps

    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app."""
        for app in self._apps:
            if app["id"] == app_id:
                return app
        return {}

    async def search_apps(
        self,
        query: str,
        limit: int = 10,
        distance_threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """
        Search for apps by a query.
        MODIFIED: This mock implementation now returns ALL available apps to ensure
        the graph always has candidates to work with. This makes the test more
        robust by focusing on the agent's selection logic rather than a brittle
        mock search.
        """
        return self._apps[:limit]

    async def list_tools(
        self,
        app_id: str,
    ) -> list[dict[str, Any]]:
        """List all tools available for a specific app."""
        return self._tools.get(app_id, [])

    async def search_tools(
        self,
        query: str,
        limit: int = 10,
        app_id: str | None = None,
        distance_threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """
        Search for tools by a query.
        MODIFIED: This mock implementation now returns all available tools for the given app_id
        to ensure robust testing of the tool selection logic, avoiding failures from a
        brittle keyword search.
        """
        if not app_id:
            # General search
            all_tools = []
            for current_app_id, tools in self._tools.items():
                for tool in tools:
                    tool_with_app_id = tool.copy()
                    tool_with_app_id["id"] = f"{current_app_id}__{tool['name']}"
                    all_tools.append(tool_with_app_id)
            return all_tools[:limit]

        # App-specific search
        all_app_tools = self._tools.get(app_id, [])
        tools_with_app_id = []
        for tool in all_app_tools:
            tool_with_app_id = tool.copy()
            tool_with_app_id["id"] = f"{app_id}__{tool['name']}"
            tools_with_app_id.append(tool_with_app_id)
        return tools_with_app_id[:limit]

    async def export_tools(
        self,
        tools: list[str] | None = None,
        format: ToolFormat = ToolFormat.NATIVE,
    ) -> list[Any]:
        """Exports a list of mock tools."""

        async def mock_send_email(to: str, body: str):
            """Sends an email."""
            return {"status": f"Email sent to {to} with body '{body}'"}

        if tools and "google_mail__send_email" in tools:
            if format == ToolFormat.NATIVE:
                return [mock_send_email]
            elif format == ToolFormat.LANGCHAIN:
                return [StructuredTool.from_function(mock_send_email)]

        async def mock_tool_callable(**kwargs: str):
            """A mock tool that confirms the task is done."""
            return {"status": "Task has been done"}

        if format == ToolFormat.NATIVE:
            return [mock_tool_callable]
        elif format == ToolFormat.LANGCHAIN:
            return [StructuredTool.from_function(mock_tool_callable)]
        else:
            raise ValueError(f"Invalid format: {format}")

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        return {"status": f"Task has been done by tool {tool_name}"}

    async def list_connected_apps(self) -> list[dict[str, str]]:
        """
        Returns a list of apps that the user has connected/authenticated.
        This is a mock function.
        """
        return [{"app_id": app_id} for app_id in self._connected_apps]


@pytest.mark.asyncio
async def test_simple_agent():
    """Tests the simple agent."""
    agent = get_agent("simple")(
        name="Test Simple",
        instructions="Test instructions",
        model="anthropic/claude-haiku-4-5",
    )
    result = await agent.invoke(user_input="What is the capital of France?")
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "paris" in last_message_text.lower()


@pytest.mark.asyncio
async def test_codeact_single_turn():
    """Tests the codeact-repl agent."""
    agent = get_agent("codeact-repl")(
        name="Test Codeact Repl",
        instructions="Test instructions",
        model="anthropic/claude-haiku-4-5",
        registry=MockToolRegistry(),
    )
    result = await agent.invoke(user_input="What is 2+2?")
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "4" in last_message_text.lower()


@pytest.mark.asyncio
async def test_codeact_multi_turn():
    """Tests the codeact-repl agent."""
    checkpoint_saver = MemorySaver()
    agent = get_agent("codeact-repl")(
        name="Test Codeact Repl",
        instructions="You are a helpful assistant",
        model="anthropic/claude-haiku-4-5",
        registry=MockToolRegistry(),
        memory=checkpoint_saver,
    )
    thread_id = str(uuid4())
    result = await agent.invoke(
        user_input="Generate a function to calculate fibonnaci number, and get 10th number in the sequence. Use fib(0) = 0 and fib(1) = 1 as the base cases. Set x = fib(10)",
        thread_id=thread_id,
    )
    assert result is not None
    last_message = result["messages"][-1]
    last_message_text = get_message_text(last_message)
    assert "55" in last_message_text.lower()
    turn2 = await agent.invoke(
        user_input="What is the x+5?",
        thread_id=thread_id,
    )
    assert turn2 is not None
    last_message2 = turn2["messages"][-1]
    last_message2_text = get_message_text(last_message2)
    assert "60" in last_message2_text.lower()
