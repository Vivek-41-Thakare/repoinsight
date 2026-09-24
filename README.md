# RepoInsight — Agentic GitHub Code Quality Analyzer

RepoInsight is a small agentic AI system that analyzes a public GitHub repository for potential code-quality and maintainability issues.

The system accepts a high-level natural-language goal, generates an execution plan using a local LLM, uses multiple tools to analyze the repository, handles a deliberately induced failure through retry/recovery, and produces a structured JSON report.
vbfbdgb
## 1. Problem Statement

Given a high-level goal such as:

> Analyze this repository and identify potential code quality issues, maintainability problems, and areas for improvement.

RepoInsight autonomously:

1. Creates an execution plan.
2. Retrieves the GitHub repository.
3. Discovers source files.
4. Reads and analyzes selected source files.
5. Calculates simple code-quality metrics.
6. Validates detected issues.
7. Recovers from a simulated tool failure.
8. Generates a structured final report.

## 2. Architecture

```text
                 ┌──────────────────┐
                 │    User Goal     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   LLM Planner    │
                 │  Ollama / LLM    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Agent Engine   │
                 └────────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │   GitHub   │  │ Code Reader│  │ Calculator │
   │    Tool    │  │    Tool    │  │    Tool    │
   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                 ┌──────────────────┐
                 │    Validation    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Recovery / Retry │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Structured JSON  │
                 │      Report      │
                 └──────────────────┘
```

## 3. Key Agentic Features

### Dynamic Planning

The planner uses a locally running Ollama LLM to convert the user's high-level goal into an actionable multi-step plan.

### Tool Use

The agent uses multiple tools:

* GitHub repository/archive tool
* Source-code reader/analyzer
* Calculator for code-quality metrics
* Validation logic
* Recovery/retry mechanism

### Failure Recovery

A GitHub repository failure is deliberately simulated during execution.

The agent detects the failure, retries the operation, and continues execution after successful recovery.

### Structured Output

The final result is returned as a JSON report containing:

* User goal
* Generated plan
* Repository information
* Tools used
* Detected issues
* Failures and recoveries
* Execution metrics

## 4. Code Quality Checks

RepoInsight performs simple static checks including:

* Lines longer than 100 characters
* TODO/FIXME markers
* Bare exception/pass patterns
* Large source files
* Files containing many functions

It also calculates:

* Total analyzed lines
* Total functions
* Issue density
* Average function size

These checks are intentionally lightweight to keep the project suitable for a small internship assessment.

## 5. Technology Stack

* Python
* Ollama
* Llama 3.2 3B
* Requests
* Pytest
* GitHub public repository/archive access

## 6. Project Structure

```text
repoinsight/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── planner.py
│   ├── executor.py
│   ├── recovery.py
│   ├── reporter.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── github_tool.py
│       ├── code_reader.py
│       └── calculator.py
│
├── tests/
│   ├── test_agent.py
│   └── test_recovery.py
│
├── examples/
│   ├── normal_run.md
│   ├── second_run.md
│   └── failure_recovery.md
│
├── docs/
│   └── architecture.md
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 7. Setup

### Step 1 — Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd repoinsight
```

### Step 2 — Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 — Install Ollama

Install Ollama and download the model:

```powershell
ollama pull llama3.2:3b
```

Make sure Ollama is running locally.

The planner uses:

```text
http://localhost:11434/api/generate
```

## 8. Run

Start the application:

```powershell
python main.py
```

Enter a high-level goal, for example:

```text
Analyze this repository and identify potential code quality issues, maintainability problems, and areas for improvement.
```

Then provide a public GitHub repository:

```text
psf/requests
```

The agent will display its planning trace, tool execution, recovery process, metrics, and final JSON report.

## 9. Example Execution

Example repository:

```text
psf/requests
```

Example execution flow:

```text
User Goal
    ↓
Dynamic LLM Plan
    ↓
GitHub Repository Tool
    ↓
Source File Discovery
    ↓
Code Reader
    ↓
Calculator
    ↓
Validation
    ↓
Simulated Failure
    ↓
Retry / Recovery
    ↓
Final JSON Report
```

A sample execution analyzed 20 source files and produced code-quality metrics including total lines, function count, issue density, and average function size.

The same execution also demonstrated a deliberately simulated GitHub timeout followed by successful retry and recovery.

## 10. Testing

Run the available tests using:

```powershell
pytest
```

The tests cover core agent/recovery behavior.

## 11. Design Decisions

### Local LLM

A local Ollama model was used for planning so that the project does not depend on a paid external LLM API.

### Lightweight Static Analysis

The code analyzer uses simple source-code heuristics instead of a large static-analysis framework. This keeps the implementation small and understandable.

### Repository Archive

Public GitHub repository archives are used to retrieve source code without requiring GitHub authentication.

### Retry-Based Recovery

A simple retry mechanism was selected because it is easy to demonstrate, test, and explain during an internship interview.

## 12. Limitations

RepoInsight is a prototype designed for an internship assessment.

Current limitations include:

* Analysis is limited to a selected number of source files.
* Code-quality checks are heuristic rather than a complete static-analysis system.
* The planner depends on a locally running Ollama model.
* The system currently focuses on public GitHub repositories.
* The generated findings should be treated as potential issues rather than definitive code-review conclusions.

## 13. Future Improvements

With additional development time, the system could be extended with:

* More sophisticated static-analysis tools
* GitHub API integration for repository metadata and commit history
* Better plan validation
* Tool-selection based on planner output
* More robust evaluation of generated findings
* Support for additional repository types and languages
* Persistent execution logs

## 14. Assessment Requirements Covered

| Requirement              | Implementation                              |
| ------------------------ | ------------------------------------------- |
| High-level goal          | CLI input                                   |
| Autonomous decomposition | Local LLM planner                           |
| Visible planning trace   | Printed execution plan                      |
| Multiple tools           | GitHub, Code Reader, Calculator, Validation |
| Failure handling         | Deliberately simulated timeout              |
| Recovery                 | Retry mechanism                             |
| Structured output        | JSON report                                 |
| Live data                | Public GitHub repository                    |
| Documentation            | README, architecture, logs, write-up        |

## 15. Author

**Vivek Thakare**

B.Tech — Artificial Intelligence & Machine Learning
JSPM University, Pune
