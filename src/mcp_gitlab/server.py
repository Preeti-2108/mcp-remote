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
HOST = os.getenv("MCP_HOST", "0.0.0.0")  # Default to all interfaces for remote access
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
    """
    CLI entrypoint for local development.

    This is called when running: uv run mcp-gitlab
    FastMCP Cloud does NOT use this - it imports the mcp object directly.
    """
    logger.info(f"Starting GitLab MCP server (Streamable HTTP) on {HOST}:{PORT}")
    mcp.run(transport="streamable-http")


# Note: FastMCP Cloud imports the mcp object and manages it directly
# For local development, use: uv run mcp-gitlab (calls main() above)
