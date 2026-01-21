"""Issue-related MCP tools."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_gitlab.gitlab_client import get_client


def register_tools(mcp: FastMCP) -> None:
    """Register all issue-related tools with the MCP server."""

    @mcp.tool()
    def list_issues(
        project_id: str,
        state: str = "opened",
        labels: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        List issues in a GitLab project.

        Args:
            project_id: Project ID or path
            state: Issue state filter ('opened', 'closed', or 'all')
            labels: Comma-separated list of labels to filter by
            limit: Maximum number of issues to return

        Returns:
            List of issues with ID, title, state, and assignee
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        kwargs = {"state": state, "per_page": limit}
        if labels:
            kwargs["labels"] = labels.split(",")

        issues = project.issues.list(**kwargs)

        if not issues:
            return f"No {state} issues found."

        result = []
        for i in issues:
            assignee = i.assignee["name"] if i.assignee else "Unassigned"
            labels_str = ", ".join(i.labels) if i.labels else "None"
            result.append(
                f"- **#{i.iid}** {i.title}\n"
                f"  State: {i.state} | Assignee: {assignee}\n"
                f"  Labels: {labels_str}\n"
                f"  URL: {i.web_url}"
            )

        return f"Found {len(issues)} issues:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_issue(project_id: str, issue_iid: int) -> str:
        """
        Get detailed information about a specific issue.

        Args:
            project_id: Project ID or path
            issue_iid: Issue IID (internal ID within the project)

        Returns:
            Detailed issue information including description and comments
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        issue = project.issues.get(issue_iid)

        assignee = issue.assignee["name"] if issue.assignee else "Unassigned"
        labels = ", ".join(issue.labels) if issue.labels else "None"

        return f"""## Issue #{issue.iid}: {issue.title}

**State:** {issue.state}
**Author:** {issue.author["name"]}
**Assignee:** {assignee}
**Labels:** {labels}
**Created:** {issue.created_at}
**Updated:** {issue.updated_at}
**URL:** {issue.web_url}

### Description

{issue.description or 'No description provided.'}
"""

    @mcp.tool()
    def create_issue(
        project_id: str,
        title: str,
        description: Optional[str] = None,
        labels: Optional[str] = None,
        assignee_ids: Optional[str] = None,
        milestone_id: Optional[int] = None,
        epic_id: Optional[int] = None,
        iteration_id: Optional[int] = None,
    ) -> str:
        """
        Create a new issue in a GitLab project.

        Args:
            project_id: Project ID or path
            title: Issue title (required)
            description: Issue description (optional, supports Markdown)
            labels: Comma-separated list of labels (optional)
            assignee_ids: Comma-separated list of user IDs to assign (optional)
            milestone_id: Milestone ID to associate with the issue (optional)
            epic_id: Epic ID to link the issue to (optional, requires GitLab Premium)
            iteration_id: Iteration ID to assign the issue to (optional, requires GitLab Premium)

        Returns:
            Confirmation with the created issue details and URL
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        # Build issue data - epic_id is handled separately via Group Epics API
        issue_data = {"title": title}
        if description:
            issue_data["description"] = description
        if labels:
            issue_data["labels"] = labels.split(",")
        if assignee_ids:
            issue_data["assignee_ids"] = [int(uid.strip()) for uid in assignee_ids.split(",")]
        if milestone_id:
            issue_data["milestone_id"] = milestone_id
        if iteration_id:
            issue_data["iteration_id"] = iteration_id

        issue = project.issues.create(issue_data)

        # Link to epic if specified (requires separate API call for group epics)
        epic_link_status = None
        if epic_id:
            try:
                # Get the group from the project's namespace
                group_id = project.namespace["id"]
                group = gl.groups.get(group_id)
                epic = group.epics.get(epic_id)
                epic.issues.create({"issue_id": issue.id})
                epic_link_status = f"**Epic:** {epic.title}"
            except Exception as e:
                epic_link_status = f"**Epic:** ⚠️ Failed to link (requires GitLab Premium): {e}"

        # Build confirmation message with assigned fields
        details = [f"**#{issue.iid}:** {issue.title}"]
        if issue.assignees:
            assignee_names = ", ".join(a["name"] for a in issue.assignees)
            details.append(f"**Assignees:** {assignee_names}")
        if issue.milestone:
            details.append(f"**Milestone:** {issue.milestone['title']}")
        if epic_link_status:
            details.append(epic_link_status)
        if hasattr(issue, "iteration") and issue.iteration:
            details.append(f"**Iteration:** {issue.iteration['title']}")
        details.append(f"**URL:** {issue.web_url}")

        return "Issue created successfully!\n\n" + "\n".join(details)

    @mcp.tool()
    def add_issue_comment(
        project_id: str,
        issue_iid: int,
        body: str,
    ) -> str:
        """
        Add a comment to an existing issue.

        Args:
            project_id: Project ID or path
            issue_iid: Issue IID to comment on
            body: Comment text (supports Markdown)

        Returns:
            Confirmation that the comment was added
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        issue = project.issues.get(issue_iid)

        note = issue.notes.create({"body": body})

        return f"Comment added to issue #{issue_iid}.\nComment ID: {note.id}"
