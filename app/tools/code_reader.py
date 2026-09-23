import re


class CodeReader:
    """
    Analyzes source code for common quality and maintainability issues.
    """

    def analyze(self, file_path: str, content: str) -> dict:
        lines = content.splitlines()

        total_lines = len(lines)
        non_empty_lines = [
            line for line in lines
            if line.strip()
        ]

        long_lines = sum(
            1
            for line in lines
            if len(line) > 100
        )

        todo_count = sum(
            1
            for line in lines
            if re.search(
                r"\b(TODO|FIXME)\b",
                line,
                re.IGNORECASE
            )
        )

        function_count = len(
            re.findall(
                r"\bdef\s+\w+|\bfunction\s+\w+",
                content
            )
        )

        class_count = len(
            re.findall(
                r"\bclass\s+\w+",
                content
            )
        )

        broad_exception_count = len(
            re.findall(
                r"except\s*:",
                content
            )
        )

        bare_pass_count = len(
            re.findall(
                r"^\s*pass\s*$",
                content,
                re.MULTILINE
            )
        )

        return {
            "file": file_path,
            "total_lines": total_lines,
            "non_empty_lines": len(non_empty_lines),
            "long_lines": long_lines,
            "todo_count": todo_count,
            "function_count": function_count,
            "class_count": class_count,
            "broad_exception_count": broad_exception_count,
            "bare_pass_count": bare_pass_count
        }