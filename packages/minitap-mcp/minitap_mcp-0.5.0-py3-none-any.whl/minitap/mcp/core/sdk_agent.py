import os

from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

# Lazy-initialized singleton agent
_agent: Agent | None = None


def get_mobile_use_agent() -> Agent:
    """Get or create the mobile-use agent singleton.

    This function lazily initializes the agent on first call, ensuring
    that CLI arguments are parsed before agent creation.
    """
    global _agent
    if _agent is None:
        config = Builders.AgentConfig
        custom_adb_socket = os.getenv("ADB_SERVER_SOCKET")
        if custom_adb_socket:
            parts = custom_adb_socket.split(":")
            if len(parts) != 3:
                raise ValueError(f"Invalid ADB server socket: {custom_adb_socket}")
            _, host, port = parts
            config = config.with_adb_server(host=host, port=int(port))
        _agent = Agent(config=config.build())
    return _agent
