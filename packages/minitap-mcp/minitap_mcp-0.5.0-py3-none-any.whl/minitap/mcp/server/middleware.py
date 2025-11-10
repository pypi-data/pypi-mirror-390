from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from minitap.mobile_use.sdk import Agent


class MaestroCheckerMiddleware(Middleware):
    def __init__(self, agent: Agent):
        self.agent = agent

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        if context.fastmcp_context:
            try:
                tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
                if "requires-maestro" in tool.tags:
                    if not self.agent.is_healthy():
                        raise ToolError(
                            "Maestro not healthy.\n"
                            "Make sure a mobile device is connected and try again."
                        )
            except Exception:
                pass
        return await call_next(context)
