"""GitLab client wrapper with environment-based configuration."""

import os
import logging
from typing import Optional

import gitlab
from dotenv import load_dotenv

# Configure logging to stderr (CRITICAL for MCP servers!)
# MCP uses STDIO for communication, so we must NEVER print to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_gitlab_client() -> gitlab.Gitlab:
    """
    Initialize and return a GitLab client.

    Reads configuration from environment variables:
    - GITLAB_URL: Your GitLab instance URL
    - GITLAB_TOKEN: Personal Access Token
    - GITLAB_SSL_VERIFY: Optional SSL verification (default: true)

    Returns:
        gitlab.Gitlab: Authenticated GitLab client

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv()

    gitlab_url = os.getenv("GITLAB_URL")
    gitlab_token = os.getenv("GITLAB_TOKEN")
    ssl_verify = os.getenv("GITLAB_SSL_VERIFY", "true").lower() == "true"

    if not gitlab_url:
        raise ValueError("GITLAB_URL environment variable is required")
    if not gitlab_token:
        raise ValueError("GITLAB_TOKEN environment variable is required")

    logger.info(f"Connecting to GitLab at {gitlab_url}")

    gl = gitlab.Gitlab(
        url=gitlab_url,
        private_token=gitlab_token,
        ssl_verify=ssl_verify,
    )

    # Validate authentication
    try:
        gl.auth()
        logger.info("Successfully authenticated with GitLab")
    except gitlab.exceptions.GitlabAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise

    return gl


# Singleton pattern for reusing the client
_client: Optional[gitlab.Gitlab] = None


def get_client() -> gitlab.Gitlab:
    """Get or create the GitLab client singleton."""
    global _client
    if _client is None:
        _client = get_gitlab_client()
    return _client
