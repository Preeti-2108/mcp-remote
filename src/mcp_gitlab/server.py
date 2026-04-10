"""Main MCP server for GitLab integration."""

import logging
from fastmcp import FastMCP

# Configure logging BEFORE importing tool modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ✅ Use FastMCP from fastmcp package (cloud-safe)
mcp = FastMCP(name="gitlab")

# Import and register tools
from mcp_gitlab.tools import projects, issues, merge_requests, pipelines, groups

projects.register_tools(mcp)
issues.register_tools(mcp)
merge_requests.register_tools(mcp)
pipelines.register_tools(mcp)
groups.register_tools(mcp)


def main() -> None:
    """
    CLI entrypoint - ONLY for local development.

    Run locally using:
    uv run mcp-gitlab
    """
    import os

    logger.info("Standalone mode - starting server with mcp.run()")

    HOST = os.getenv("MCP_HOST", "0.0.0.0")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    logger.info(f"Starting GitLab MCP server on {HOST}:{PORT}")

    # ✅ Safe for local only
    mcp.run(
        transport="http",
        host=HOST,
        port=PORT,
    )


# ❌ NO asyncio.run
# ❌ NO async def app()
# ❌ NO manual loop handling
