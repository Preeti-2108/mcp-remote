"""Pipeline and CI/CD-related MCP tools."""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_gitlab.gitlab_client import get_client


def register_tools(mcp: FastMCP) -> None:
    """Register all pipeline-related tools with the MCP server."""

    @mcp.tool()
    def list_pipelines(
        project_id: str,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """
        List CI/CD pipelines in a GitLab project.

        Args:
            project_id: Project ID or path
            status: Filter by status ('running', 'pending', 'success', 'failed', 'canceled')
            limit: Maximum number of pipelines to return

        Returns:
            List of pipelines with ID, status, branch, and duration
        """
        gl = get_client()
        project = gl.projects.get(project_id)

        kwargs = {"per_page": limit}
        if status:
            kwargs["status"] = status

        pipelines = project.pipelines.list(**kwargs)

        if not pipelines:
            return "No pipelines found."

        result = []
        for p in pipelines:
            duration = f"{p.duration}s" if p.duration else "N/A"
            result.append(
                f"- **Pipeline #{p.id}**\n"
                f"  Status: {p.status} | Ref: {p.ref}\n"
                f"  Duration: {duration}\n"
                f"  Created: {p.created_at}"
            )

        return f"Found {len(pipelines)} pipelines:\n\n" + "\n\n".join(result)

    @mcp.tool()
    def get_pipeline(project_id: str, pipeline_id: int) -> str:
        """
        Get detailed information about a specific pipeline.

        Args:
            project_id: Project ID or path
            pipeline_id: Pipeline ID

        Returns:
            Detailed pipeline information including stages and timing
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)

        duration = f"{pipeline.duration}s" if pipeline.duration else "N/A"
        queued = (
            f"{pipeline.queued_duration}s" if pipeline.queued_duration else "N/A"
        )

        return f"""## Pipeline #{pipeline.id}

**Status:** {pipeline.status}
**Ref:** {pipeline.ref}
**SHA:** {pipeline.sha[:8]}
**Created:** {pipeline.created_at}
**Started:** {pipeline.started_at or 'Not started'}
**Finished:** {pipeline.finished_at or 'Not finished'}
**Duration:** {duration}
**Queued Duration:** {queued}
**URL:** {pipeline.web_url}
"""

    @mcp.tool()
    def list_pipeline_jobs(project_id: str, pipeline_id: int) -> str:
        """
        List all jobs in a pipeline.

        Args:
            project_id: Project ID or path
            pipeline_id: Pipeline ID

        Returns:
            List of jobs with name, stage, status, and duration
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)

        jobs = pipeline.jobs.list(get_all=True)

        if not jobs:
            return "No jobs found in this pipeline."

        # Group jobs by stage
        stages: dict = {}
        for job in jobs:
            stage = job.stage
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(job)

        result = [f"## Jobs in Pipeline #{pipeline_id}\n"]

        for stage, stage_jobs in stages.items():
            result.append(f"\n### Stage: {stage}\n")
            for job in stage_jobs:
                duration = f"{job.duration:.1f}s" if job.duration else "N/A"
                status_emoji = {
                    "success": "[OK]",
                    "failed": "[FAILED]",
                    "running": "[RUNNING]",
                    "pending": "[PENDING]",
                    "canceled": "[CANCELED]",
                    "skipped": "[SKIPPED]",
                }.get(job.status, f"[{job.status.upper()}]")

                result.append(
                    f"- {status_emoji} **{job.name}** (ID: {job.id})\n"
                    f"  Duration: {duration}"
                )

        return "\n".join(result)

    @mcp.tool()
    def get_job_log(project_id: str, job_id: int) -> str:
        """
        Get the log output of a CI/CD job.

        Args:
            project_id: Project ID or path
            job_id: Job ID

        Returns:
            The job log output (may be truncated for very long logs)
        """
        gl = get_client()
        project = gl.projects.get(project_id)
        job = project.jobs.get(job_id)

        try:
            log = job.trace().decode("utf-8")

            # Truncate very long logs
            max_length = 10000
            if len(log) > max_length:
                log = log[-max_length:]
                log = f"[... truncated, showing last {max_length} characters ...]\n\n{log}"

            return f"## Job Log: {job.name} (ID: {job_id})\n\n```\n{log}\n```"
        except Exception as e:
            return f"Error retrieving job log: {e}"
