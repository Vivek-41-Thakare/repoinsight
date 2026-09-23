import json


class Reporter:
    """
    Generates the final structured report
    produced by the RepoInsight agent.
    """

    def generate_report(
        self,
        goal,
        plan,
        repository,
        tools_used,
        issues,
        failures,
        execution_summary
    ):
        """
        Build and return the final structured JSON report.
        """

        # -----------------------------------------------------
        # Determine final status
        # -----------------------------------------------------

        if execution_summary.get("files_analyzed", 0) > 0:
            status = "completed"

        elif execution_summary.get("files_discovered", 0) > 0:
            status = "completed_with_warnings"

        else:
            status = "failed"

        # -----------------------------------------------------
        # Build report
        # -----------------------------------------------------

        report = {
            "goal": goal,

            "status": status,

            "plan": plan,

            "repository": repository,

            "tools_used": tools_used,

            "issues": issues,

            "failures": failures,

            "execution_summary": execution_summary
        }

        # -----------------------------------------------------
        # Convert to readable JSON
        # -----------------------------------------------------

        return json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        )