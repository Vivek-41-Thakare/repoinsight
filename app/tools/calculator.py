class Calculator:
    """
    Calculator tool used by RepoInsight Agent
    for code-quality metrics.
    """

    def issue_density(self, issues: int, total_lines: int) -> float:
        """
        Calculate issues per 100 lines of code.
        """

        if total_lines <= 0:
            return 0.0

        density = (issues / total_lines) * 100

        return round(density, 2)

    def average_function_size(
        self,
        total_lines: int,
        function_count: int
    ) -> float:
        """
        Calculate average lines per function.
        """

        if function_count <= 0:
            return 0.0

        average = total_lines / function_count

        return round(average, 2)