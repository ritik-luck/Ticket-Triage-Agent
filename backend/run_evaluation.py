from evaluation.evaluator import evaluation_runner


def print_evaluation_summary(summary: dict) -> None:

    print("\n========== Ticket Triage Agent Evaluation ==========\n")

    print(f"Total Tests  : {summary['total_tests']}")
    print(f"Passed Tests : {summary['passed_tests']}")
    print(f"Failed Tests : {summary['failed_tests']}")
    print(f"Pass Rate    : {summary['pass_rate']}%")
    print(f"Total Time   : {summary['total_time_seconds']} seconds")

    print("\n================ Test Results ================\n")

    for result in summary["results"]:
        status = "PASSED" if result["passed"] else "FAILED"

        print(f"[{status}] {result['name']}")

        if "checks" in result:
            for check in result["checks"]:
                check_status = "OK" if check["passed"] else "NOT OK"
                print(f"  - {check['check']}: {check_status}")

                if not check["passed"]:
                    print(f"    Expected: {check.get('expected')}")
                    print(f"    Actual  : {check.get('actual')}")

        if "error" in result:
            print(f"  Error: {result['error']}")

        print()

    print("Evaluation report saved to: memory/evaluation_report.json")


if __name__ == "__main__":
    summary = evaluation_runner.run_all_tests()
    print_evaluation_summary(summary)