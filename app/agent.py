from app.planner import Planner
from app.tools.github_tool import GitHubTool
from app.tools.code_reader import CodeReader
from app.tools.calculator import Calculator
from app.recovery import RecoveryManager
from app.reporter import Reporter


class RepoInsightAgent:
    """
    Main agentic workflow for RepoInsight.

    The agent:
    1. Creates a dynamic plan using a local LLM.
    2. Retrieves repository information.
    3. Discovers source files.
    4. Reads and analyzes source code.
    5. Calculates code-quality metrics.
    6. Validates detected issues.
    7. Recovers from tool failures.
    8. Generates a structured final report.
    """

    def __init__(self, simulate_failure=False):
        self.planner = Planner()
        self.github = GitHubTool()
        self.code_reader = CodeReader()
        self.calculator = Calculator()
        self.recovery = RecoveryManager()
        self.reporter = Reporter()
        self.simulate_failure = simulate_failure

    def run(self, goal: str, repo_url: str):

        print("\n" + "=" * 60)
        print("REPOINSIGHT AGENT")
        print("=" * 60)

        print("\nGOAL:")
        print(goal)

        # ---------------------------------------------------------
        # STEP 1: Dynamic Planning
        # ---------------------------------------------------------

        plan = self.planner.create_plan(goal)

        print("\nAGENT PLAN:")

        for i, step in enumerate(plan, start=1):
            print(f"{i}. {step}")

        # ---------------------------------------------------------
        # STEP 2: Parse Repository
        # ---------------------------------------------------------

        repo_url = repo_url.strip().rstrip("/")

        if repo_url.startswith("https://github.com/"):
            repo_path = repo_url.replace(
                "https://github.com/",
                ""
            ).strip("/")

        elif repo_url.startswith("http://github.com/"):
            repo_path = repo_url.replace(
                "http://github.com/",
                ""
            ).strip("/")

        else:
            repo_path = repo_url

        parts = repo_path.split("/")

        if len(parts) < 2:
            raise ValueError(
                "Repository must be in owner/repository format "
                "or a GitHub URL."
            )

        owner = parts[0]
        repo = parts[1]

        # ---------------------------------------------------------
        # STEP 3: GitHub Repository Tool
        # ---------------------------------------------------------

        print("\n[TOOL] GitHub Repository")

        def get_repository():

            if self.simulate_failure:
                self.simulate_failure = False

                raise RuntimeError(
                    "Simulated GitHub API timeout "
                    "for recovery test"
                )

            return self.github.get_repo_info(
                owner,
                repo
            )

        repo_info = self.recovery.execute_with_recovery(
            tool_name="github_repository",
            operation=get_repository
        )

        # ---------------------------------------------------------
        # STEP 4: Discover Source Files
        # ---------------------------------------------------------

        print(
            "\n[TOOL] GitHub Recursive File Discovery"
        )

        files = self.recovery.execute_with_recovery(
            tool_name="github_file_listing",
            operation=lambda: self.github.list_source_files(
                owner,
                repo
            )
        )

        source_extensions = (
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".php",
            ".rb"
        )

        source_files = [
            file
            for file in files
            if file["type"] == "file"
            and file["name"]
            .lower()
            .endswith(source_extensions)
        ]

        # Limit analysis so very large repositories
        # do not take excessive time.

        MAX_FILES = 20

        source_files = source_files[:MAX_FILES]

        print(
            f"[DISCOVERY] Found "
            f"{len(source_files)} "
            f"source files to analyze."
        )

        # ---------------------------------------------------------
        # STEP 5: Read and Analyze Source Code
        # ---------------------------------------------------------

        print("\n[TOOL] GitHub File Reader")

        analyzed_files = []

        all_issues = []

        for file in source_files:

            file_path = file["path"]

            print(
                f"[ANALYZING] {file_path}"
            )

            try:

                content = self.recovery.execute_with_recovery(
                    tool_name="code_reader",
                    operation=lambda p=file_path:
                        self.github.get_file_content(
                            owner,
                            repo,
                            p
                        )
                )

                analysis = self.code_reader.analyze(
                    file_path,
                    content
                )

                analyzed_files.append(
                    analysis
                )

                # -------------------------------------------------
                # Detect long lines
                # -------------------------------------------------

                if analysis.get(
                    "long_lines",
                    0
                ) > 0:

                    all_issues.append({
                        "file": file_path,
                        "type": "long_lines",
                        "severity": "medium",
                        "details": (
                            f"{analysis['long_lines']} "
                            "lines exceed 100 characters."
                        )
                    })

                # -------------------------------------------------
                # Detect TODO / FIXME
                # -------------------------------------------------

                if analysis.get(
                    "todo_count",
                    0
                ) > 0:

                    all_issues.append({
                        "file": file_path,
                        "type": "todo",
                        "severity": "low",
                        "details": (
                            f"{analysis['todo_count']} "
                            "TODO/FIXME markers found."
                        )
                    })

                # -------------------------------------------------
                # Detect broad exception handling
                # -------------------------------------------------

                if analysis.get(
                    "broad_exception_count",
                    0
                ) > 0:

                    all_issues.append({
                        "file": file_path,
                        "type": "broad_exception",
                        "severity": "medium",
                        "details": (
                            f"{analysis['broad_exception_count']} "
                            "bare exception handler(s) found."
                        )
                    })

                # -------------------------------------------------
                # Detect bare pass statements
                # -------------------------------------------------

                if analysis.get(
                    "bare_pass_count",
                    0
                ) > 0:

                    all_issues.append({
                        "file": file_path,
                        "type": "bare_pass",
                        "severity": "low",
                        "details": (
                            f"{analysis['bare_pass_count']} "
                            "bare pass statement(s) found."
                        )
                    })

                # -------------------------------------------------
                # Detect large files
                # -------------------------------------------------

                if analysis.get(
                    "total_lines",
                    0
                ) > 500:

                    all_issues.append({
                        "file": file_path,
                        "type": "large_file",
                        "severity": "medium",
                        "details": (
                            f"Large source file with "
                            f"{analysis['total_lines']} "
                            "lines."
                        )
                    })

                # -------------------------------------------------
                # Detect excessive functions
                # -------------------------------------------------

                if analysis.get(
                    "function_count",
                    0
                ) > 30:

                    all_issues.append({
                        "file": file_path,
                        "type": "many_functions",
                        "severity": "medium",
                        "details": (
                            f"File contains "
                            f"{analysis['function_count']} "
                            "functions."
                        )
                    })

            except Exception as error:

                print(
                    f"[WARNING] Could not analyze "
                    f"{file_path}: {error}"
                )

        # ---------------------------------------------------------
        # STEP 6: Calculator Tool
        # ---------------------------------------------------------

        print("\n[TOOL] Calculator")

        total_lines = sum(
            item.get(
                "total_lines",
                0
            )
            for item in analyzed_files
        )

        total_issues = len(
            all_issues
        )

        issue_density = (
            self.calculator.issue_density(
                total_issues,
                total_lines
            )
        )

        total_functions = sum(
            item.get(
                "function_count",
                0
            )
            for item in analyzed_files
        )

        average_function_size = (
            self.calculator.average_function_size(
                total_lines,
                total_functions
            )
        )

        print(
            f"[METRIC] Total analyzed lines: "
            f"{total_lines}"
        )

        print(
            f"[METRIC] Total functions: "
            f"{total_functions}"
        )

        print(
            f"[METRIC] Issue density: "
            f"{issue_density}%"
        )

        print(
            f"[METRIC] Average function size: "
            f"{average_function_size} lines"
        )

        # ---------------------------------------------------------
        # STEP 7: Validation
        # ---------------------------------------------------------

        print(
            "\n[VALIDATION] "
            "Checking detected issues..."
        )

        validated_issues = []

        for issue in all_issues:

            if issue.get("file"):

                issue["validated"] = True

                validated_issues.append(
                    issue
                )

        print(
            f"[VALIDATION] "
            f"{len(validated_issues)} "
            "issues validated."
        )

        # ---------------------------------------------------------
        # STEP 8: Recovery Summary
        # ---------------------------------------------------------

        recovery_summary = (
            self.recovery.get_summary()
        )

        # ---------------------------------------------------------
        # STEP 9: Execution Summary
        # ---------------------------------------------------------

        execution_summary = {

            "steps_completed": len(plan),

            "tools_called": 6,

            "files_discovered": len(files),

            "files_analyzed": len(
                analyzed_files
            ),

            "issues_detected": len(
                validated_issues
            ),

            "total_lines_analyzed": (
                total_lines
            ),

            "total_functions": (
                total_functions
            ),

            "issue_density_percent": (
                issue_density
            ),

            "average_function_size": (
                average_function_size
            ),

            "failures": (
                recovery_summary[
                    "failures"
                ]
            ),

            "recoveries": (
                recovery_summary[
                    "recoveries"
                ]
            )
        }

        # ---------------------------------------------------------
        # STEP 10: Final Structured Report
        # ---------------------------------------------------------

        report = (
            self.reporter.generate_report(
                goal=goal,

                plan=plan,

                repository=repo_info,

                tools_used=[
                    "github_repository",
                    "github_file_listing",
                    "github_file_reader",
                    "code_reader",
                    "calculator",
                    "validation",
                    "recovery_manager"
                ],

                issues=validated_issues,

                failures=(
                    recovery_summary[
                        "failure_details"
                    ]
                ),

                execution_summary=(
                    execution_summary
                )
            )
        )

        # ---------------------------------------------------------
        # FINAL OUTPUT
        # ---------------------------------------------------------

        print(
            "\n" + "=" * 60
        )

        print(
            "REPOINSIGHT FINAL REPORT"
        )

        print(
            "=" * 60
        )

        print(report)

        return report