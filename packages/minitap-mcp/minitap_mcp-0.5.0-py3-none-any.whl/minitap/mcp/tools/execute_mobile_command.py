"""Tool for running manual tasks on a connected mobile device."""

from collections.abc import Mapping
from typing import Any

from fastmcp.exceptions import ToolError
from minitap.mobile_use.sdk.types import ManualTaskConfig
from minitap.mobile_use.sdk.types.task import PlatformTaskRequest
from pydantic import Field

from minitap.mcp.core.decorators import handle_tool_errors
from minitap.mcp.core.sdk_agent import get_mobile_use_agent
from minitap.mcp.main import mcp


def _serialize_result(result: Any) -> Any:
    """Convert SDK responses to serializable data for MCP."""
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    if isinstance(result, Mapping):
        return dict(result)
    return result


@mcp.tool(
    name="execute_mobile_command",
    tags={"requires-maestro"},
    description="""
    Execute a natural language command on a mobile device using the Minitap SDK.
    This tool allows you to control your Android or iOS device using natural language.
    Examples:
    - "Open the settings app and tell me the battery level"
    - "Find the first 3 unread emails in Gmail"
    - "Take a screenshot and save it"
    
    The tool uses the Minitap platform with API key authentication.
    Set MINITAP_API_KEY and MINITAP_API_BASE_URL environment variables.
    Visit https://platform.minitap.ai to get your API key.
    """,
)
@handle_tool_errors
async def execute_mobile_command(
    goal: str = Field(description="High-level goal describing the action to perform."),
    output_description: str | None = Field(
        default=None,
        description="Optional description of the expected output format. "
        "For example: 'A JSON array with sender and subject for each email' "
        "or 'The battery percentage as a number'.",
    ),
    profile: str = Field(
        default="default",
        description="Name of the profile to use for this task. Defaults to 'default'.",
    ),
) -> str | dict[str, Any]:
    """Run a manual task on a mobile device via the Minitap platform."""
    try:
        request = PlatformTaskRequest(
            task=ManualTaskConfig(goal=goal, output_description=output_description),
        )
        agent = get_mobile_use_agent()
        result = await agent.run_task(request=request)
        return _serialize_result(result)
    except Exception as e:
        raise ToolError(str(e))
