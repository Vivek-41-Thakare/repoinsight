from app.recovery import RecoveryManager


def test_recovery_retries_after_failure():
    recovery = RecoveryManager(max_retries=1)

    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1

        if attempts["count"] == 1:
            raise RuntimeError("temporary failure")

        return "success"

    result = recovery.execute_with_recovery(
        tool_name="test_tool",
        operation=operation
    )

    assert result == "success"
    assert attempts["count"] == 2

    summary = recovery.get_summary()

    assert summary["failures"] == 1
    assert summary["recoveries"] == 1
