# MCP GitLab On-Premise

An MCP (Model Context Protocol) server that enables Claude to interact with your GitLab On-Premise instance. This server provides 18 tools for managing projects, issues, merge requests, and CI/CD pipelines directly from Claude.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A GitLab Personal Access Token

## Installation

1. Clone the repository:
   ```bash
   git clone https://innersource.soprasteria.com/i2s-ics-do/dps_mcp_local_gitlab.git
   cd dps_mcp_local_gitlab
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## GitLab Token Setup

Create a Personal Access Token on your GitLab instance:

1. Go to `https://your-gitlab.com/-/user_settings/personal_access_tokens`
2. Create a new token with the appropriate scopes:

| Use Case | Required Scopes |
|----------|-----------------|
| Full access (read + write) | `api` |
| Read-only access | `read_api` + `read_repository` |

## Configuring Claude Code

### Option 1: CLI Command (Recommended)

Add the MCP server to Claude Code using the command line:

```bash
claude mcp add gitlab \
  --transport stdio \
  --env GITLAB_URL=https://your-gitlab.com \
  --env GITLAB_TOKEN=glpat-xxxxxxxxxxxx \
  -- uv --directory /path/to/dps_mcp_local_gitlab run mcp-gitlab
```

Replace:
- `https://your-gitlab.com` with your GitLab instance URL
- `glpat-xxxxxxxxxxxx` with your Personal Access Token
- `/path/to/dps_mcp_local_gitlab` with the absolute path to this repository

### Option 2: Project Configuration File (.mcp.json)

Create a `.mcp.json` file in your project root to share the configuration with your team:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "uv",
      "args": ["--directory", "/path/to/dps_mcp_local_gitlab", "run", "mcp-gitlab"],
      "env": {
        "GITLAB_URL": "${GITLAB_URL}",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"
      }
    }
  }
}
```

Then set the environment variables in your shell or `.env` file:
```bash
export GITLAB_URL=https://your-gitlab.com
export GITLAB_TOKEN=glpat-xxxxxxxxxxxx
```

### Option 3: Claude Desktop Configuration

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "uv",
      "args": ["--directory", "/path/to/dps_mcp_local_gitlab", "run", "mcp-gitlab"],
      "env": {
        "GITLAB_URL": "https://your-gitlab.com",
        "GITLAB_TOKEN": "glpat-xxxxxxxxxxxx"
      }
    }
  }
}
```

### Useful Claude Code Commands

```bash
claude mcp list          # List all configured MCP servers
claude mcp get gitlab    # View gitlab MCP configuration details
claude mcp remove gitlab # Remove the gitlab MCP server
```

## SSL Configuration

For self-signed certificates, add the `GITLAB_SSL_VERIFY` environment variable:

```bash
claude mcp add gitlab \
  --transport stdio \
  --env GITLAB_URL=https://your-gitlab.com \
  --env GITLAB_TOKEN=glpat-xxxxxxxxxxxx \
  --env GITLAB_SSL_VERIFY=false \
  -- uv --directory /path/to/dps_mcp_local_gitlab run mcp-gitlab
```

## Available Tools

### Projects & Repositories (6 tools)
| Tool | Description |
|------|-------------|
| `list_projects` | List accessible projects |
| `get_project` | Get project details |
| `list_branches` | List branches in a project |
| `list_commits` | List commits |
| `get_file` | Read a file from the repository |
| `list_repository_tree` | List files and directories |

### Issues (4 tools)
| Tool | Description |
|------|-------------|
| `list_issues` | List project issues |
| `get_issue` | Get issue details |
| `create_issue` | Create a new issue |
| `add_issue_comment` | Add a comment to an issue |

### Merge Requests (4 tools)
| Tool | Description |
|------|-------------|
| `list_merge_requests` | List merge requests |
| `get_merge_request` | Get MR details |
| `get_merge_request_changes` | View MR diff |
| `add_mr_comment` | Add a comment to an MR |

### Pipelines CI/CD (4 tools)
| Tool | Description |
|------|-------------|
| `list_pipelines` | List CI/CD pipelines |
| `get_pipeline` | Get pipeline details |
| `list_pipeline_jobs` | List jobs in a pipeline |
| `get_job_log` | View job logs |

## Usage Examples

Once configured, you can ask Claude to interact with your GitLab instance:

- *"List all my GitLab projects"*
- *"Show me the open issues in project my-team/my-project"*
- *"Get the diff for merge request !42 in project my-team/my-project"*
- *"Why did pipeline #123 fail in project my-team/my-project?"*
- *"Create an issue titled 'Fix login bug' in project my-team/my-project"*

## Troubleshooting

### "GITLAB_URL environment variable is required"
Make sure you've configured the environment variables correctly when adding the MCP server.

### Authentication failed
Verify that your Personal Access Token is valid and has the required scopes.

### SSL certificate errors
If using self-signed certificates, set `GITLAB_SSL_VERIFY=false` in your MCP configuration.
