"""Group-related MCP tools for labels, milestones, and iterations."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_gitlab.gitlab_client import get_client


def format_label(label) -> str:
    """Format a single label into a markdown string."""
    return f"- **{label.name}**"


def register_tools(mcp: FastMCP) -> None:
    """Register all group-related tools with the MCP server."""

    @mcp.tool()
    def list_groups(
        search: Optional[str] = None,
        owned: bool = False,
        limit: int = 20,
    ) -> str:
        """
        List GitLab groups accessible to the authenticated user.

        Args:
            search: Optional search term to filter groups by name
            owned: If true, only list groups owned by the user
            limit: Maximum number of groups to return (default: 20)

        Returns:
            Formatted list of groups with ID, name, and URL
        """
        gl = get_client()

        kwargs = {"per_page": limit}
        if search:
            kwargs["search"] = search
        if owned:
            kwargs["owned"] = True

        groups = gl.groups.list(**kwargs)

        if not groups:
            return "No groups found."

        result = []
        for g in groups:
            result.append(
                f"- **{g.name}** (ID: {g.id})\n"
                f"  Path: {g.full_path}\n"
                f"  URL: {g.web_url}\n"
                f"  Description: {g.description or 'No description'}"
            )

        return f"Found {len(groups)} groups:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_group(group_id: str) -> str:
        """
        Get detailed information about a specific GitLab group.

        Args:
            group_id: Group ID (numeric) or path (e.g., 'my-group' or 'parent/child')

        Returns:
            Detailed group information including description and stats
        """
        gl = get_client()
        group = gl.groups.get(group_id)

        return f"""## {group.name}

**ID:** {group.id}
**Path:** {group.full_path}
**Description:** {group.description or 'No description'}
**URL:** {group.web_url}
**Visibility:** {group.visibility}
**Created:** {group.created_at}
**Projects:** {getattr(group, 'projects_count', 'N/A')}
**Members:** {getattr(group, 'members_count', 'N/A')}
"""

    @mcp.tool()
    def list_group_labels(
        group_id: str,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        """
        List labels defined at the group level.

        Args:
            group_id: Group ID or path
            search: Optional search term to filter labels by name
            limit: Maximum number of labels to return (default: 50)

        Returns:
            List of group labels with name, color, and description
        """
        gl = get_client()
        group = gl.groups.get(group_id)

        kwargs = {"per_page": limit}
        if search:
            kwargs["search"] = search

        labels = group.labels.list(**kwargs)

        if not labels:
            return "No labels found in this group."

        result = []
        for label in labels:
            formatted = format_label(label)
            if formatted:
                result.append(formatted)

        return f"Found {len(labels)} labels:\n\n" + "\n".join(result)

    @mcp.tool()
    def create_group_label(
        group_id: str,
        name: str,
        color: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Create a new label at the group level.

        Args:
            group_id: Group ID or path
            name: Label name (required)
            color: Label color in hex format (e.g., '#FF0000')
            description: Optional label description

        Returns:
            Confirmation with the created label details
        """
        gl = get_client()
        group = gl.groups.get(group_id)

        label_data = {"name": name, "color": color}
        if description:
            label_data["description"] = description

        label = group.labels.create(label_data)

        return f"""Label created successfully!

**Name:** {label.name}
**Color:** {label.color}
**Description:** {label.description or 'No description'}
"""

    @mcp.tool()
    def list_group_milestones(
        group_id: str,
        state: str = "active",
        search: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        List milestones defined at the group level.

        Args:
            group_id: Group ID or path
            state: Milestone state filter ('active', 'closed', or 'all')
            search: Optional search term to filter milestones
            limit: Maximum number of milestones to return

        Returns:
            List of group milestones with title, dates, and progress
        """
        gl = get_client()
        group = gl.groups.get(group_id)

        kwargs = {"per_page": limit, "state": state}
        if search:
            kwargs["search"] = search

        milestones = group.milestones.list(**kwargs)

        if not milestones:
            return f"No {state} milestones found in this group."

        result = []
        for m in milestones:
            dates = ""
            if m.start_date:
                dates += f"Start: {m.start_date}"
            if m.due_date:
                dates += f" | Due: {m.due_date}"
            dates = dates or "No dates set"

            result.append(
                f"- **{m.title}** (ID: {m.id})\n"
                f"  State: {m.state} | {dates}\n"
                f"  Description: {(m.description or 'No description')[:100]}"
            )

        return f"Found {len(milestones)} milestones:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_group_milestone(group_id: str, milestone_id: int) -> str:
        """
        Get detailed information about a specific group milestone.

        Args:
            group_id: Group ID or path
            milestone_id: Milestone ID

        Returns:
            Detailed milestone information including description and dates
        """
        gl = get_client()
        group = gl.groups.get(group_id)
        milestone = group.milestones.get(milestone_id)

        return f"""## Milestone: {milestone.title}

**ID:** {milestone.id}
**State:** {milestone.state}
**Start Date:** {milestone.start_date or 'Not set'}
**Due Date:** {milestone.due_date or 'Not set'}
**URL:** {milestone.web_url}

### Description

{milestone.description or 'No description provided.'}
"""

    @mcp.tool()
    def list_group_iterations(
        group_id: str,
        state: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        List iterations defined at the group level.

        Args:
            group_id: Group ID or path
            state: Iteration state filter ('upcoming', 'current', 'closed', or None for all)
            limit: Maximum number of iterations to return

        Returns:
            List of group iterations with title, dates, and state
        """
        gl = get_client()
        group = gl.groups.get(group_id)

        kwargs = {"per_page": limit}
        if state:
            kwargs["state"] = state

        iterations = group.iterations.list(**kwargs)

        if not iterations:
            state_msg = f" with state '{state}'" if state else ""
            return f"No iterations found{state_msg} in this group."

        result = []
        for it in iterations:
            dates = f"{it.start_date} - {it.due_date}" if it.start_date else "No dates"
            result.append(
                f"- **{it.title}** (ID: {it.id})\n"
                f"  State: {it.state} | {dates}"
            )

        return f"Found {len(iterations)} iterations:\n\n" + "\n".join(result)
