"""Tests for deterministic 3-state TSAR adoption response classification."""

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "tsar-conformance"
    / "adoption_response.py"
)
SPEC = importlib.util.spec_from_file_location("tsar_adoption_response", MODULE)
assert SPEC is not None and SPEC.loader is not None
adoption_response = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = adoption_response
SPEC.loader.exec_module(adoption_response)

AdoptionEvaluation = adoption_response.AdoptionEvaluation
AdoptionOutcome = adoption_response.AdoptionOutcome
MandatoryCheck = adoption_response.MandatoryCheck
NonBlockingIssue = adoption_response.NonBlockingIssue
OptionalCheck = adoption_response.OptionalCheck
classify_and_format_adoption = adoption_response.classify_and_format_adoption


class TestAdoptionResponse(unittest.TestCase):
    """Validate all 3 adoption outcome states and edge cases."""

    def test_01_complete_adoption_all_mandatory_passed_no_warnings(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
                MandatoryCheck(name="policy-validation", passed=True, executed=True),
            ],
            optional_checks=[
                OptionalCheck(name="telemetry-hook", executed=True, available=True, passed=True),
            ],
            non_blocking_issues=[],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(
            result.message,
            "✅ Adoption successful. Let's start working on your project.",
        )

    def test_02_successful_mandatory_with_non_blocking_warnings(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
            non_blocking_issues=[
                NonBlockingIssue(
                    summary="Optional pre-commit hook not installed",
                    impact="Local commits will not auto-run TSAR lint",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertTrue(
            result.message.startswith("⚠️ Adoption successful, but some issues require attention.")
        )
        self.assertIn("Optional pre-commit hook not installed", result.message)
        self.assertIn("Local commits will not auto-run TSAR lint", result.message)
        self.assertIn("governance-files", result.message)

    def test_03_inaccessible_tsar_repository(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=False,
            repository_error="HTTP 403 Forbidden",
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("HTTP 403 Forbidden", result.message)

    def test_04_missing_mandatory_governance_file(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=["AGENTS.md", "policies/tsar.yaml"],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("AGENTS.md", result.message)
        self.assertIn("policies/tsar.yaml", result.message)

    def test_05_failed_mandatory_validation(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(
                    name="schema-validation",
                    passed=False,
                    executed=True,
                    details="fail_closed missing",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("schema-validation", result.message)
        self.assertIn("fail_closed missing", result.message)

    def test_06_mandatory_verification_not_executed(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(
                    name="conformance-suite",
                    passed=False,
                    executed=False,
                    details="runner skipped",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertIn("conformance-suite", result.message)

    def test_07_optional_verification_unavailable_after_successful_mandatory(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
            optional_checks=[
                OptionalCheck(
                    name="sbom-attestation",
                    executed=False,
                    available=False,
                    details="cosign not installed",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS_WITH_WARNINGS)
        self.assertTrue(
            result.message.startswith("⚠️ Adoption successful, but some issues require attention.")
        )
        self.assertIn("sbom-attestation", result.message)
        self.assertIn("governance-files", result.message)

    def test_08_no_additional_text_after_exact_success_message(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(len(result.message.splitlines()), 1)
        self.assertEqual(len(result.lines), 1)
        self.assertFalse(result.message.endswith("\n"))

    def test_09_mandatory_failure_mixed_with_non_blocking_warning(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[
                MandatoryCheck(name="governance-files", passed=True, executed=True),
                MandatoryCheck(name="policy-check", passed=False, executed=True),
            ],
            non_blocking_issues=[
                NonBlockingIssue(
                    summary="Optional badge missing",
                    impact="README badge will not render",
                ),
            ],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))
        self.assertNotIn("⚠️", result.message)

    def test_10_empty_mandatory_checks_no_false_positive_success(self) -> None:
        evaluation = AdoptionEvaluation(
            repository_accessible=True,
            missing_mandatory_files=[],
            mandatory_checks=[],
            optional_checks=[],
            non_blocking_issues=[],
        )
        result = classify_and_format_adoption(evaluation)
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertTrue(result.message.startswith("❌ Adoption failed."))


if __name__ == "__main__":
    unittest.main()
