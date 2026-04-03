"""Cloud deployment entry point - exports mcp object only, never calls mcp.run()."""

from mcp_gitlab.server import mcp

# This module exists solely for cloud deployment
# It imports and re-exports the mcp object without any main() function
# that could interfere with the cloud platform's lifecycle management

__all__ = ["mcp"]
