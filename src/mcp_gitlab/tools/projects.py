"""Project and repository-related MCP tools."""

import base64
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_gitlab.gitlab_client import get_client


def register_tools(mcp: FastMCP) -> None:
    """Register all project-related tools with the MCP server."""

    @mcp.tool()
    def list_projects(
        search: Optional[str] = None,
        owned: bool = False,
        limit: int = 20,
    ) -> str:
        """
        List GitLab projects accessible to the authenticated user.

        Args:
            search: Optional search term to filter projects by name
            owned: If true, only list projects owned by the user
            limit: Maximum number of projects to return (default: 20)

        Returns:
            Formatted list of projects with ID, name, and URL
        """
        gl = get_client()

        kwargs = {"per_page": limit}
        if search:
            kwargs["search"] = search
        if owned:
            kwargs["owned"] = True

        projects = gl.projects.list(**kwargs)

        if not projects:
            return "No projects found."

        result = []
        for p in projects:
            result.append(
                f"- **{p.name}** (ID: {p.id})\n"
                f"  Path: {p.path_with_namespace}\n"
                f"  URL: {p.web_url}\n"
                f"  Description: {p.description or 'No description'}"
            )

        return f"Found {len(projects)} projects:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_project(project_id: str) -> str:
        """
        Get detailed information about a specific GitLab project.

        Args:
            project_id: Project ID (numeric) or path (e.g., 'namespace/project-name')

        Returns:
            Detailed project information including description, stats, and URLs
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        return f"""## {project.name}

**ID:** {project.id}
**Path:** {project.path_with_namespace}
**Description:** {project.description or 'No description'}
**URL:** {project.web_url}
**Default Branch:** {project.default_branch}
**Visibility:** {project.visibility}
**Created:** {project.created_at}
**Last Activity:** {project.last_activity_at}
**Stars:** {project.star_count}
**Forks:** {project.forks_count}
"""

    @mcp.tool()
    def list_branches(
        project_id: str,
        search: Optional[str] = None,
    ) -> str:
        """
        List branches in a GitLab project.

        Args:
            project_id: Project ID or path
            search: Optional search term to filter branches

        Returns:
            List of branch names with their latest commit info
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        kwargs = {"get_all": True}
        if search:
            kwargs["search"] = search

        branches = project.branches.list(**kwargs)

        if not branches:
            return "No branches found."

        result = []
        for b in branches:
            protected = " (protected)" if b.protected else ""
            commit_title = b.commit["title"][:50] if b.commit else "No commit"
            commit_id = b.commit["short_id"] if b.commit else "N/A"
            result.append(
                f"- **{b.name}**{protected}\n"
                f"  Last commit: {commit_id} - {commit_title}"
            )

        return f"Found {len(branches)} branches:\n\n" + "\n".join(result)

    @mcp.tool()
    def list_commits(
        project_id: str,
        ref_name: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        List commits in a GitLab project.

        Args:
            project_id: Project ID or path
            ref_name: Branch or tag name to list commits from
            since: Only commits after this date (ISO 8601 format, e.g., '2024-01-01')
            limit: Maximum number of commits to return

        Returns:
            List of commits with hash, author, date, and message
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        kwargs = {"per_page": limit}
        if ref_name:
            kwargs["ref_name"] = ref_name
        if since:
            kwargs["since"] = since

        commits = project.commits.list(**kwargs)

        if not commits:
            return "No commits found."

        result = []
        for c in commits:
            result.append(
                f"- **{c.short_id}** by {c.author_name}\n"
                f"  Date: {c.created_at}\n"
                f"  Message: {c.title}"
            )

        return f"Found {len(commits)} commits:\n\n" + "\n".join(result)

    @mcp.tool()
    def get_file(
        project_id: str,
        file_path: str,
        ref: str = "main",
    ) -> str:
        """
        Get the contents of a file from a GitLab repository.

        Args:
            project_id: Project ID or path
            file_path: Path to the file in the repository
            ref: Branch, tag, or commit SHA (default: 'main')

        Returns:
            The decoded file contents
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        try:
            f = project.files.get(file_path=file_path, ref=ref)
            content = base64.b64decode(f.content).decode("utf-8")
            return f"**File:** {file_path} (ref: {ref})\n\n```\n{content}\n```"
        except Exception as e:
            return f"Error reading file: {e}"

    @mcp.tool()
    def list_repository_tree(
        project_id: str,
        path: str = "",
        ref: Optional[str] = None,
    ) -> str:
        """
        List files and directories in a repository.

        Args:
            project_id: Project ID or path
            path: Directory path to list (empty for root)
            ref: Branch, tag, or commit SHA (optional)

        Returns:
            List of files and directories with their types
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        kwargs = {}
        if path:
            kwargs["path"] = path
        if ref:
            kwargs["ref"] = ref

        items = project.repository_tree(**kwargs)

        if not items:
            return "No files found in this path."

        dirs = [i for i in items if i["type"] == "tree"]
        files = [i for i in items if i["type"] == "blob"]

        result = []
        if dirs:
            result.append("**Directories:**")
            for d in dirs:
                result.append(f"  - {d['name']}/")
        if files:
            result.append("\n**Files:**")
            for f in files:
                result.append(f"  - {f['name']}")

        return "\n".join(result)
