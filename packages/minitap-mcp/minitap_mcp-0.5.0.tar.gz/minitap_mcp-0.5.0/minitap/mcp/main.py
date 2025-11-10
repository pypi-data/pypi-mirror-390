"""MCP server for mobile-use with screen analysis capabilities."""

import argparse
import os
import sys
import threading

# Fix Windows console encoding for Unicode characters (emojis in logs)
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        import colorama

        colorama.init(strip=False, convert=True, wrap=True)
    except ImportError:
        pass


from fastmcp import FastMCP  # noqa: E402
from minitap.mobile_use.config import settings as sdk_settings

from minitap.mcp.core.config import settings  # noqa: E402
from minitap.mcp.core.device import DeviceInfo  # noqa: E402
from minitap.mcp.core.device import list_available_devices
from minitap.mcp.core.logging_config import (
    configure_logging,  # noqa: E402
    get_logger,
)
from minitap.mcp.server.middleware import MaestroCheckerMiddleware
from minitap.mcp.server.poller import device_health_poller

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))


def main() -> None:
    """Main entry point for the MCP server."""

    parser = argparse.ArgumentParser(description="Mobile Use MCP Server")
    parser.add_argument("--api-key", type=str, required=False, default=None)
    parser.add_argument("--llm-profile", type=str, required=False, default=None)
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as network server (uses MCP_SERVER_HOST and MCP_SERVER_PORT from env)",
    )
    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=None,
        help="Port to run the server on (overrides MCP_SERVER_PORT env variable)",
    )

    args = parser.parse_args()

    if args.api_key:
        os.environ["MINITAP_API_KEY"] = args.api_key
        settings.__init__()
        sdk_settings.__init__()

    if args.llm_profile:
        os.environ["MINITAP_LLM_PROFILE_NAME"] = args.llm_profile
        settings.__init__()
        sdk_settings.__init__()

    if args.port:
        os.environ["MCP_SERVER_PORT"] = str(args.port)
        settings.__init__()
        sdk_settings.__init__()

    if not settings.MINITAP_API_KEY:
        raise ValueError("Minitap API key is required to run the MCP")

    # Run MCP server with optional host/port for remote access
    if args.server:
        logger.info(f"Starting MCP server on {settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
        mcp_lifespan(
            transport="http",
            host=settings.MCP_SERVER_HOST,
            port=settings.MCP_SERVER_PORT,
        )
    else:
        logger.info("Starting MCP server in local mode")
        mcp_lifespan()


logger = get_logger(__name__)

mcp = FastMCP(
    name="mobile-use-mcp",
    instructions="""
        This server provides analysis tools for connected
        mobile devices (iOS or Android).
        Call get_available_devices() to list them.
    """,
)
from minitap.mcp.tools import analyze_screen  # noqa: E402, F401
from minitap.mcp.tools import compare_screenshot_with_figma  # noqa: E402, F401
from minitap.mcp.tools import execute_mobile_command  # noqa: E402, F401
from minitap.mcp.tools import save_figma_assets  # noqa: E402, F401


@mcp.resource("data://devices")
def get_available_devices() -> list[DeviceInfo]:
    """Provides a list of connected mobile devices (iOS or Android)."""
    return list_available_devices()


def mcp_lifespan(**mcp_run_kwargs):
    from minitap.mcp.core.sdk_agent import get_mobile_use_agent  # noqa: E402

    agent = get_mobile_use_agent()
    mcp.add_middleware(MaestroCheckerMiddleware(agent))

    # Start device health poller in background
    logger.info("Device health poller started")
    stop_event = threading.Event()
    poller_thread = threading.Thread(
        target=device_health_poller,
        args=(
            stop_event,
            agent,
        ),
        daemon=True,
    )
    poller_thread.start()

    try:
        mcp.run(**mcp_run_kwargs)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
    finally:
        # Stop device health poller
        logger.info("Stopping device health poller...")
        stop_event.set()

        # Give the poller thread a reasonable time to stop gracefully
        poller_thread.join(timeout=10.0)

        if poller_thread.is_alive():
            logger.warning("Device health poller thread did not stop gracefully")
        else:
            logger.info("Device health poller stopped successfully")
