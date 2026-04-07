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
# NOTE: Do NOT pass host/port here - they're only for mcp.run() in local mode
# For cloud deployment, the platform manages the transport layer
mcp = FastMCP("gitlab")

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
    CLI entrypoint - ONLY for standalone local development.

    This should NEVER be called automatically. It's explicitly invoked when
    running: uv run mcp-gitlab

    For cloud deployment, the platform MUST use the 'mcp' object directly,
    not this main() function.
    """
    import os

    # This function should only run when explicitly called by the CLI tool,
    # not during module import or when fastmcp is managing the server.
    logger.info("Standalone mode - starting server with mcp.run()")

    HOST = os.getenv("MCP_HOST", "0.0.0.0")  # Default to all interfaces
    PORT = int(os.getenv("MCP_PORT", "8000"))  # Default port 8000

    logger.info(f"Starting GitLab MCP server (Streamable HTTP) on {HOST}:{PORT}")
    mcp.run(transport="streamable-http", host=HOST, port=PORT)

async def app():
    return mcp
