"""Main MCP server for GitLab integration."""

import logging

from mcp.server.fastmcp import FastMCP

# Configure logging BEFORE importing tool modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with name "gitlab"
# This name appears in Claude's tool list as the server identifier
# Configure host and port for remote access
# - host="0.0.0.0" allows connections from any network interface
# - host="127.0.0.1" restricts to localhost only (safer for local testing)
import os
HOST = os.getenv("MCP_HOST", "0.0.0.0")  # Default to all interfaces for remote access.
PORT = int(os.getenv("MCP_PORT", "8000"))  # Default port 8000

mcp = FastMCP("gitlab", host=HOST, port=PORT)

# Import and register tools from each module
# Each module has a register_tools(mcp) function that adds its tools
from mcp_gitlab.tools import projects, issues, merge_requests, pipelines, groups

projects.register_tools(mcp)
issues.register_tools(mcp)
merge_requests.register_tools(mcp)
pipelines.register_tools(mcp)
groups.register_tools(mcp)


def main() -> None:
    """Run the MCP server."""

    # ============================================================================
    # LOCAL SERVER (STDIO) - Original implementation
    # ============================================================================
    # Uncomment this for local STDIO transport (spawned by Claude Code)
    # logger.info("Starting GitLab MCP server (STDIO)...")
    # mcp.run(transport="stdio")

    # ============================================================================
    # REMOTE SERVER (HTTP/SSE) - For network access
    # ============================================================================
    # Choose one of the options below:

    # Option 1: SSE Transport (Server-Sent Events)
    # - Supports real-time streaming updates
    # - Better for long-lived connections
    # - Recommended for production
    # logger.info("Starting GitLab MCP server (SSE)")
    # mcp.run(transport="sse")

    # Option 2: Streamable HTTP Transport (Active)
    # - Simple request/response
    # - Stateless
    # - Good for basic operations
    # Note: FastMCP uses default port 8000 and binds to 0.0.0.0
    # Set environment variables to customize:
    #   - MCP_HOST: Host to bind to (default: 0.0.0.0)
    #   - MCP_PORT: Port to listen on (default: 8000)
    logger.info("Starting GitLab MCP server (Streamable HTTP)")
    mcp.run(transport="streamable-http")

    # Note: By default binds to 0.0.0.0:8000 (accessible from network)
    #       Set MCP_HOST=127.0.0.1 to restrict to localhost only (safer for testing)


if __name__ == "__main__":
    main()
