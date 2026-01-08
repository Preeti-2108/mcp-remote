"""Merge request-related MCP tools."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_gitlab.gitlab_client import get_client


def register_tools(mcp: FastMCP) -> None:
    """Register all merge request-related tools with the MCP server."""

    @mcp.tool()
    def list_merge_requests(
        project_id: str,
        state: str = "opened",
        limit: int = 20,
    ) -> str:
        """
        List merge requests in a GitLab project.

        Args:
            project_id: Project ID or path
            state: MR state filter ('opened', 'merged', 'closed', or 'all')
            limit: Maximum number of MRs to return

        Returns:
            List of merge requests with ID, title, source/target branches
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        mrs = project.mergerequests.list(state=state, per_page=limit)

        if not mrs:
            return f"No {state} merge requests found."

        result = []
        for mr in mrs:
            result.append(
                f"- **!{mr.iid}** {mr.title}\n"
                f"  {mr.source_branch} -> {mr.target_branch}\n"
                f"  State: {mr.state} | Author: {mr.author['name']}\n"
                f"  URL: {mr.web_url}"
            )

        return f"Found {len(mrs)} merge requests:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_merge_request(project_id: str, mr_iid: int) -> str:
        """
        Get detailed information about a specific merge request.

        Args:
            project_id: Project ID or path
            mr_iid: Merge request IID (internal ID within the project)

        Returns:
            Detailed MR information including description, commits, and status
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)

        labels = ", ".join(mr.labels) if mr.labels else "None"
        assignee = mr.assignee["name"] if mr.assignee else "Unassigned"

        return f"""## Merge Request !{mr.iid}: {mr.title}

**State:** {mr.state}
**Author:** {mr.author["name"]}
**Assignee:** {assignee}
**Source Branch:** {mr.source_branch}
**Target Branch:** {mr.target_branch}
**Labels:** {labels}
**Created:** {mr.created_at}
**Updated:** {mr.updated_at}
**URL:** {mr.web_url}

### Description

{mr.description or 'No description provided.'}

### Merge Status

- **Mergeable:** {mr.merge_status}
- **Has Conflicts:** {mr.has_conflicts}
- **Changes Count:** {mr.changes_count}
"""

    @mcp.tool()
    def get_merge_request_changes(project_id: str, mr_iid: int) -> str:
        """
        Get the diff/changes for a merge request.

        Args:
            project_id: Project ID or path
            mr_iid: Merge request IID

        Returns:
            Summary of files changed with additions and deletions
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)

        changes = mr.changes()

        if not changes.get("changes"):
            return "No changes found in this merge request."

        result = [f"## Changes in !{mr_iid}\n"]

        for change in changes["changes"]:
            old_path = change.get("old_path", "")
            new_path = change.get("new_path", "")

            if change.get("new_file"):
                status = "[NEW]"
            elif change.get("deleted_file"):
                status = "[DELETED]"
            elif change.get("renamed_file"):
                status = f"[RENAMED from {old_path}]"
            else:
                status = "[MODIFIED]"

            result.append(f"- {status} `{new_path}`")

        return "\n".join(result)

    @mcp.tool()
    def add_mr_comment(
        project_id: str,
        mr_iid: int,
        body: str,
    ) -> str:
        """
        Add a comment to a merge request.

        Args:
            project_id: Project ID or path
            mr_iid: Merge request IID
            body: Comment text (supports Markdown)

        Returns:
            Confirmation that the comment was added
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)

        note = mr.notes.create({"body": body})

        return f"Comment added to merge request !{mr_iid}.\nComment ID: {note.id}"
