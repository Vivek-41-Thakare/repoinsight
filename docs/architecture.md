# RepoInsight Architecture

## 1. System Overview

RepoInsight is a small agentic AI system designed to analyze public GitHub repositories for potential code-quality and maintainability issues.

The system follows a simple planning → execution → validation → recovery → reporting workflow.

## 2. Architecture Diagram

```text
┌──────────────────────────────┐
│          USER                │
│                              │
│ High-level natural language  │
│ goal + GitHub repository     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       LLM PLANNER            │
│                              │
│ Ollama + Llama 3.2 3B        │
│ Generates execution plan     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       AGENT ENGINE           │
│                              │
│ Executes planned operations  │
└──────────────┬───────────────┘
               │
       ┌───────┼────────┐
       │       │        │
       ▼       ▼        ▼
┌──────────┐ ┌────────┐ ┌────────────┐
│ GitHub   │ │ Code   │ │ Calculator │
│ Tool     │ │ Reader │ │ Tool       │
└────┬─────┘ └────┬───┘ └──────┬─────┘
     │            │             │
     └────────────┼─────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │    VALIDATION    │
        │                  │
        │ Validate detected│
        │ potential issues │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ RECOVERY MANAGER │
        │                  │
        │ Detect failure   │
        │ Retry operation  │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │     REPORTER     │
        │                  │
        │ Structured JSON  │
        │ final report     │
        └──────────────────┘
```

## 3. Component Responsibilities

### User

Provides:

* A natural-language goal.
* A public GitHub repository.

Example:

```text
Goal:
Analyze this repository and identify potential code quality issues.

Repository:
psf/requests
```

### LLM Planner

The planner uses the locally running Llama 3.2 3B model through Ollama.

Its responsibility is to convert the high-level goal into a sequence of actionable steps.

The generated plan is displayed to the user before execution.

### Agent Engine

The agent engine coordinates the complete workflow.

It:

1. Receives the generated plan.
2. Parses the GitHub repository.
3. Calls the required tools.
4. Collects tool outputs.
5. Performs validation.
6. Handles failures through the recovery manager.
7. Sends the results to the reporter.

### GitHub Tool

The GitHub tool retrieves a public repository archive and discovers relevant source files.

It also reads individual source files for analysis.

### Code Reader

The code reader performs lightweight static checks.

Current checks include:

* Long lines
* TODO/FIXME markers
* Bare exception/pass patterns
* Large source files
* Files containing many functions

### Calculator

The calculator computes simple metrics:

* Total analyzed lines
* Issue density
* Average function size

### Validation

Detected issues are checked before being included in the final report.

The current validation ensures that detected issues contain a source file reference before they are added to the validated results.

### Recovery Manager

The recovery manager handles tool failures.

For the assessment demonstration, the GitHub operation intentionally raises a simulated timeout.

The recovery manager then retries the operation.

If the retry succeeds, execution continues normally.

### Reporter

The reporter creates the final structured JSON output.

The report contains:

* Goal
* Execution plan
* Repository information
* Tools used
* Detected issues
* Failure/recovery information
* Execution metrics

## 4. Execution Flow

The complete execution flow is:

```text
1. User enters goal
        ↓
2. User enters GitHub repository
        ↓
3. LLM generates execution plan
        ↓
4. Agent displays plan
        ↓
5. GitHub repository is retrieved
        ↓
6. Source files are discovered
        ↓
7. Source files are read
        ↓
8. Code-quality checks are performed
        ↓
9. Metrics are calculated
        ↓
10. Issues are validated
        ↓
11. Failures are recovered using retry
        ↓
12. Final JSON report is generated
```

## 5. Failure Recovery Flow

A deliberate failure is included to demonstrate robustness.

```text
GitHub Tool
     │
     ▼
Simulated Timeout
     │
     ▼
Recovery Manager
     │
     ▼
Retry
     │
     ├── Failure ──→ Report Failure
     │
     └── Success
           │
           ▼
      Continue Agent
           │
           ▼
      Final Report
```

## 6. Design Philosophy

The architecture intentionally remains small and modular.

The system separates:

* Planning
* Tool execution
* Code analysis
* Metric calculation
* Validation
* Recovery
* Reporting

This makes each component easier to understand, test, and replace without introducing unnecessary complexity.

## 7. Current Scope

RepoInsight is an internship-assessment prototype rather than a production code-review platform.

The current architecture focuses on demonstrating the core properties of an agentic system:

* Planning
* Tool use
* Multi-step execution
* Error recovery
* Structured reporting

More advanced capabilities can be added later without changing the basic control flow.
