# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that enables Claude to interact with GitLab On-Premise instances. It provides 18 tools for managing projects, issues, merge requests, and CI/CD pipelines.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server (STDIO transport)
uv run mcp-gitlab

# Install in development mode
uv pip install -e .
```

## Architecture

### Core Components

- **`src/mcp_gitlab/server.py`**: FastMCP server entry point. Initializes the `FastMCP("gitlab")` instance and registers tools from each module via `register_tools(mcp)` pattern.

- **`src/mcp_gitlab/gitlab_client.py`**: Singleton GitLab client wrapper. Uses `python-gitlab` library with environment-based configuration. The `get_client()` function returns a cached authenticated client.

- **`src/mcp_gitlab/tools/`**: Tool modules organized by GitLab domain:
  - `projects.py`: 6 tools (list_projects, get_project, list_branches, list_commits, get_file, list_repository_tree)
  - `issues.py`: 4 tools (list_issues, get_issue, create_issue, add_issue_comment)
  - `merge_requests.py`: 4 tools (list_merge_requests, get_merge_request, get_merge_request_changes, add_mr_comment)
  - `pipelines.py`: 4 tools (list_pipelines, get_pipeline, list_pipeline_jobs, get_job_log)

### Tool Registration Pattern

Each tool module exports a `register_tools(mcp: FastMCP)` function that defines tools using the `@mcp.tool()` decorator. Tools are nested functions that get registered when called.

### Configuration

Environment variables (loaded via python-dotenv):
- `GITLAB_URL`: GitLab instance URL (required)
- `GITLAB_TOKEN`: Personal Access Token (required)
- `GITLAB_SSL_VERIFY`: SSL verification, set to "false" for self-signed certs (default: "true")

## MCP-Specific Constraints

- **Never use `print()`** - MCP uses STDIO for communication; use `logging` to stderr instead
- **Type hints** generate tool parameter schemas automatically
- **Docstrings** become tool descriptions visible to Claude
- **Parameters with defaults** are treated as optional
- Tools should return Markdown-formatted strings for best readability

## Integration with Claude

```bash
# Add to Claude Code
claude mcp add gitlab \
  --transport stdio \
  --env GITLAB_URL=https://your-gitlab.com \
  --env GITLAB_TOKEN=glpat-your-token \
  -- uv --directory /path/to/this/repo run mcp-gitlab
```
