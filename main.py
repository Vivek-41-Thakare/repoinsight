from app.agent import RepoInsightAgent


def main():
    print("=" * 60)
    print("REPOINSIGHT - AGENTIC GITHUB CODE QUALITY ANALYZER")
    print("=" * 60)

    print("\nEnter a high-level goal for the agent.")
    print("Example:")
    print("Analyze this repository and identify potential code quality issues.")

    goal = input("\nGoal: ").strip()

    if not goal:
        goal = (
            "Analyze this repository and identify "
            "potential code quality issues."
        )

    print("\nEnter GitHub repository.")

    print("Examples:")
    print("  psf/requests")
    print("  https://github.com/psf/requests")

    repo_url = input("\nRepository: ").strip()

    if not repo_url:
        print("\n[ERROR] Repository cannot be empty.")
        return

    print("\nStarting RepoInsight Agent...")

    # ---------------------------------------------------------
    # CREATE AGENT
    # simulate_failure=True deliberately causes one failure
    # so the recovery mechanism can be demonstrated.
    # ---------------------------------------------------------

    agent = RepoInsightAgent(
        simulate_failure=True
    )

    try:

        # -----------------------------------------------------
        # RUN AGENT
        # -----------------------------------------------------

        report = agent.run(
            goal=goal,
            repo_url=repo_url
        )

        # -----------------------------------------------------
        # COMPLETION MESSAGE
        # -----------------------------------------------------

        print("\n" + "=" * 60)
        print("AGENT EXECUTION COMPLETED")
        print("=" * 60)

        print(
            "\nThe agent successfully completed the requested "
            "repository analysis."
        )

    except KeyboardInterrupt:

        print("\n\n[STOPPED] Agent execution cancelled by user.")

    except Exception as error:

        print("\n" + "=" * 60)
        print("AGENT EXECUTION FAILED")
        print("=" * 60)

        print(f"\nError: {error}")

        print(
            "\nPlease check:"
            "\n1. GitHub repository name"
            "\n2. Internet connection"
            "\n3. GitHub API availability"
            "\n4. Repository permissions"
        )


if __name__ == "__main__":
    main()