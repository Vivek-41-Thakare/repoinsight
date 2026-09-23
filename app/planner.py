import json
import requests


class Planner:
    """
    Local LLM-based planner using Ollama.
    """

    def __init__(self):
        self.model = "llama3.2:3b"
        self.url = "http://localhost:11434/api/generate"

    def create_plan(self, goal: str) -> list[str]:
        prompt = f"""
You are the planning component of an agentic
GitHub repository code quality analyzer.

User goal:
{goal}

Available tools:
1. GitHub repository tool
2. Code reader tool
3. Calculator tool
4. Validation tool
5. Recovery/retry mechanism
6. Report generator

Create a concise execution plan.

Rules:
- Generate 5 to 7 steps.
- Steps must be actionable.
- Use the available tools where appropriate.
- Include validation.
- Include failure recovery.
- End with final report generation.
- Do not explain the plan.
- Return ONLY valid JSON.

Format:
{{
  "steps": [
    "step 1",
    "step 2",
    "step 3"
  ]
}}
"""

        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=120
            )

            response.raise_for_status()

            result = response.json()

            raw_output = result.get(
                "response",
                ""
            ).strip()

            data = json.loads(raw_output)

            steps = data.get("steps", [])

            if not steps:
                raise ValueError(
                    "Ollama returned an empty plan."
                )

            print(
                f"[PLANNER] Dynamic plan generated "
                f"using local model: {self.model}"
            )

            return steps

        except Exception as error:
            print(
                f"[PLANNER ERROR] {error}"
            )

            print(
                "[PLANNER] Using fallback plan."
            )

            return self._fallback_plan()

    def _fallback_plan(self):
        return [
            "Validate the GitHub repository",
            "Retrieve repository metadata",
            "Discover relevant source files",
            "Read and analyze selected source files",
            "Calculate code quality metrics",
            "Validate detected issues",
            "Generate a structured final report"
        ]