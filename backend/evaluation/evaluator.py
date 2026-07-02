import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import requests
from evaluation.testcases import TEST_CASES


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
REPORT_DIR = Path("memory")
REPORT_FILE = REPORT_DIR / "evaluation_report.json"
REQUEST_TIMEOUT_SECONDS = 180


class EvaluationRunner:

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.triage_url = f"{self.base_url}/triage"
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def run_all_tests(self) -> Dict[str, Any]:

        results = []

        start_time = time.time()

        for test_case in TEST_CASES:
            result = self.run_test(test_case)
            results.append(result)

        end_time = time.time()

        total_tests = len(results)
        passed_tests = sum(1 for result in results if result["passed"])
        failed_tests = total_tests - passed_tests

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": round((passed_tests / total_tests) * 100, 2) if total_tests else 0,
            "total_time_seconds": round(end_time - start_time, 2),
            "results": results
        }

        self.save_report(summary)

        return summary

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        test_name = test_case["name"]
        request_body = test_case["request"]

        try:
            start_time = time.time()

            response = requests.post(
                self.triage_url,
                json=request_body,
                timeout=REQUEST_TIMEOUT_SECONDS
            )

            end_time = time.time()

            response_time = round(end_time - start_time, 2)

            if response.status_code != 200:
                return {
                    "name": test_name,
                    "passed": False,
                    "response_time_seconds": response_time,
                    "error": f"Expected status code 200 but got {response.status_code}",
                    "response_text": response.text
                }

            response_json = response.json()

            validation_result = self.validate_response(
                test_case=test_case,
                response_json=response_json
            )

            return {
                "name": test_name,
                "passed": validation_result["passed"],
                "response_time_seconds": response_time,
                "checks": validation_result["checks"],
                "actual_response": response_json
            }

        except requests.exceptions.Timeout as error:
            return {
                "name": test_name,
                "passed": False,
                "error": (
                    f"Request timed out after {REQUEST_TIMEOUT_SECONDS} seconds. "
                    f"Backend likely took too long to respond: {error}"
                )
            }

        except requests.exceptions.RequestException as error:
            return {
                "name": test_name,
                "passed": False,
                "error": f"HTTP request failed: {error}"
            }

        except Exception as error:
            return {
                "name": test_name,
                "passed": False,
                "error": str(error)
            }

    def validate_response(
        self,
        test_case: Dict[str, Any],
        response_json: Dict[str, Any]
    ) -> Dict[str, Any]:

        checks = []

        checks.append(
            self.check_required_fields(response_json)
        )

        checks.append(
            self.check_expected_value(
                field_name="category",
                actual_value=response_json.get("category"),
                expected_value=test_case.get("expected_category")
            )
        )

        checks.append(
            self.check_expected_value(
                field_name="assigned_team",
                actual_value=response_json.get("assigned_team"),
                expected_value=test_case.get("expected_team")
            )
        )

        checks.append(
            self.check_expected_value(
                field_name="web_search_used",
                actual_value=response_json.get("web_search_used"),
                expected_value=test_case.get("expected_web_search_used")
            )
        )

        if "expected_priority" in test_case:
            checks.append(
                self.check_expected_value(
                    field_name="priority",
                    actual_value=response_json.get("priority"),
                    expected_value=test_case.get("expected_priority")
                )
            )

        if "expected_guardrail_applied" in test_case:
            checks.append(
                self.check_expected_value(
                    field_name="guardrail_applied",
                    actual_value=response_json.get("guardrail_applied"),
                    expected_value=test_case.get("expected_guardrail_applied")
                )
            )

        if "expected_escalation_required" in test_case:
            checks.append(
                self.check_expected_value(
                    field_name="escalation_required",
                    actual_value=response_json.get("escalation_required"),
                    expected_value=test_case.get("expected_escalation_required")
                )
            )

        if "expected_sla_breach_risk" in test_case:
            checks.append(
                self.check_expected_value(
                    field_name="sla_breach_risk",
                    actual_value=response_json.get("sla_breach_risk"),
                    expected_value=test_case.get("expected_sla_breach_risk")
                )
            )

        checks.append(
            self.check_non_empty_list(
                field_name="suggested_solution",
                actual_value=response_json.get("suggested_solution")
            )
        )

        checks.append(
            self.check_non_empty_list(
                field_name="audit_trail",
                actual_value=response_json.get("audit_trail")
            )
        )

        passed = all(check["passed"] for check in checks)

        return {
            "passed": passed,
            "checks": checks
        }

    def check_required_fields(self, response_json: Dict[str, Any]) -> Dict[str, Any]:
        required_fields = [
            "ticket_id",
            "category",
            "confidence",
            "priority",
            "assigned_team",
            "rag_used",
            "rag_score",
            "rag_sources",
            "web_search_used",
            "suggested_solution",
            "recommended_action",
            "audit_trail"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in response_json
        ]

        return {
            "check": "required_fields",
            "passed": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }

    def check_expected_value(
        self,
        field_name: str,
        actual_value: Any,
        expected_value: Any
    ) -> Dict[str, Any]:

        if isinstance(expected_value, list):
            passed = actual_value in expected_value
        else:
            passed = actual_value == expected_value

        return {
            "check": field_name,
            "passed": passed,
            "expected": expected_value,
            "actual": actual_value
        }

    def check_non_empty_list(
        self,
        field_name: str,
        actual_value: Any
    ) -> Dict[str, Any]:

        passed = isinstance(actual_value, list) and len(actual_value) > 0

        return {
            "check": field_name,
            "passed": passed,
            "actual_count": len(actual_value) if isinstance(actual_value, list) else 0
        }

    def save_report(self, summary: Dict[str, Any]) -> None:
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            json.dump(summary, file, indent=4)


evaluation_runner = EvaluationRunner(
    base_url=os.getenv("TRIAGE_API_BASE_URL", DEFAULT_BASE_URL)
)
