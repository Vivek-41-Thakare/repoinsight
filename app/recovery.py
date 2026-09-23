class RecoveryManager:
    def __init__(self, max_retries=1):
        self.max_retries = max_retries
        self.failures = []
        self.recoveries = 0

    def execute_with_recovery(self, tool_name, operation, fallback=None):
        try:
            return operation()
        except Exception as first_error:
            failure_record = {
                "tool": tool_name,
                "error": str(first_error),
                "attempts": 1,
                "recovered": False,
                "recovery_method": None
            }

            print(f"\n[ERROR] {tool_name}: {first_error}")

            for attempt in range(1, self.max_retries + 1):
                print(
                    f"[RECOVERY] Retrying {tool_name} "
                    f"(attempt {attempt}/{self.max_retries})..."
                )

                try:
                    result = operation()

                    failure_record["attempts"] = attempt + 1
                    failure_record["recovered"] = True
                    failure_record["recovery_method"] = "retry"

                    self.failures.append(failure_record)
                    self.recoveries += 1

                    print(f"[SUCCESS] {tool_name} recovered successfully.")
                    return result

                except Exception as retry_error:
                    failure_record["attempts"] = attempt + 1
                    failure_record["error"] = str(retry_error)

                    print(f"[RECOVERY FAILED] {retry_error}")

            if fallback is not None:
                print(f"[RECOVERY] Using fallback for {tool_name}...")

                try:
                    result = fallback()

                    failure_record["recovered"] = True
                    failure_record["recovery_method"] = "fallback"

                    self.failures.append(failure_record)
                    self.recoveries += 1

                    print(
                        f"[SUCCESS] Fallback recovery completed for {tool_name}."
                    )
                    return result

                except Exception as fallback_error:
                    failure_record["error"] = str(fallback_error)
                    failure_record["recovery_method"] = "fallback_failed"

                    self.failures.append(failure_record)
                    raise

            failure_record["recovery_method"] = "retry_failed"
            self.failures.append(failure_record)
            raise

    def get_summary(self):
        return {
            "failures": len(self.failures),
            "recoveries": self.recoveries,
            "failure_details": self.failures
        }

    def reset(self):
        self.failures = []
        self.recoveries = 0
