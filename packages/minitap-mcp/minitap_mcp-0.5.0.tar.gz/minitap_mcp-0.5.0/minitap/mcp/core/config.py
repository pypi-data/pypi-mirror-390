"""Configuration for the MCP server."""

from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv(verbose=True)


class MCPSettings(BaseSettings):
    """Configuration class for MCP server."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Minitap API configuration
    MINITAP_API_KEY: SecretStr | None = Field(default=None)
    MINITAP_API_BASE_URL: str = Field(default="https://platform.minitap.ai/api/v1")
    OPEN_ROUTER_API_KEY: SecretStr | None = Field(default=None)

    VISION_MODEL: str = Field(default="qwen/qwen-2.5-vl-7b-instruct")

    # Figma MCP server configuration
    FIGMA_MCP_SERVER_URL: str = Field(default="http://127.0.0.1:3845/mcp")

    # MCP server configuration (optional, for remote access)
    MCP_SERVER_HOST: str = Field(default="0.0.0.0")
    MCP_SERVER_PORT: int = Field(default=8000)


settings = MCPSettings()  # type: ignore
