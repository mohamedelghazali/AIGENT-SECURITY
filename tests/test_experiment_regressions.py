"""Regression tests reproducing the 11 experimental TSAR adoption scenarios."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_ADOPTION_PATH = (
    REPO_ROOT / "tools" / "tsar-conformance" / "verify_adoption.py"
)

_SPEC = importlib.util.spec_from_file_location(
    "tsar_verify_adoption", VERIFY_ADOPTION_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
verify_adoption = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = verify_adoption
_SPEC.loader.exec_module(verify_adoption)

AdoptionOutcome = verify_adoption.AdoptionOutcome
AdoptionRunInput = verify_adoption.AdoptionRunInput
RuntimeCapabilities = verify_adoption.RuntimeCapabilities
evaluate_adoption_run = verify_adoption.evaluate_adoption_run
verify_local_repository_checkout = verify_adoption.verify_local_repository_checkout

ALL_CORE_FILES = {path: True for path in verify_adoption.CORE_FILES}


class ExperimentRegressionTests(unittest.TestCase):
    """9 regression tests covering all 11 experimental adoption scenarios."""

    def test_01_workstation_full_adoption_success(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=True,
                runner_passed=True,
                consultation_verifier_executed=True,
                consultation_verifier_passed=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(
            result.rendered.splitlines()[0],
            "✅ Adoption successful. Let's start working on your project.",
        )

    def test_02_web_only_false_positive_prevention(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files=dict(ALL_CORE_FILES),
            )
        )
        self.assertNotEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(result.outcome, AdoptionOutcome.WARNING)
        self.assertEqual(
            result.rendered.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )

    def test_03_web_only_false_negative_prevention(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=False,
                consultation_verifier_executed=False,
            )
        )
        self.assertNotEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.outcome, AdoptionOutcome.WARNING)
        self.assertEqual(
            result.rendered.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )

    def test_04_missing_system_directives_fail_closed(self) -> None:
        incomplete_files = dict(ALL_CORE_FILES)
        incomplete_files["system/CORE_DIRECTIVE.md"] = False
        incomplete_files["system/ENFORCEMENT_LEVELS.md"] = False
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files=incomplete_files,
                llms_full_fallback_used=False,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.rendered.splitlines()[0], "❌ Adoption failed.")

    def test_05_llms_full_fallback_recovery(self) -> None:
        without_system_dir = {
            path: (not path.startswith("system/"))
            for path in verify_adoption.CORE_FILES
        }
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                    directory_crawling_blocked=True,
                    raw_host_blocked=True,
                    github_api_available=True,
                ),
                verified_files=without_system_dir,
                llms_full_fallback_used=True,
                llms_full_verified_directives=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.WARNING)
        self.assertEqual(
            result.rendered.splitlines()[0],
            "⚠️ Adoption successful, but some issues require attention.",
        )

    def test_06_inaccessible_repository_fail_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=False,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=False,
                    has_python_runtime=False,
                ),
                verified_files={},
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.rendered.splitlines()[0], "❌ Adoption failed.")

    def test_07_local_skipped_runner_fail_closed(self) -> None:
        result = evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=True,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
                verified_files=dict(ALL_CORE_FILES),
                runner_executed=False,
                consultation_verifier_executed=True,
                consultation_verifier_passed=True,
            )
        )
        self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
        self.assertEqual(result.rendered.splitlines()[0], "❌ Adoption failed.")

    def test_08_weakened_security_posture_rejected(self) -> None:
        for kwargs in (
            {"fail_closed": False},
            {"default_mode": "advisory"},
            {"allow_advisory_fallback": True},
        ):
            result = evaluate_adoption_run(
                AdoptionRunInput(
                    repository_accessible=True,
                    capabilities=RuntimeCapabilities(
                        has_local_checkout=True,
                        has_python_runtime=True,
                    ),
                    verified_files=dict(ALL_CORE_FILES),
                    runner_executed=True,
                    runner_passed=True,
                    consultation_verifier_executed=True,
                    consultation_verifier_passed=True,
                    **kwargs,
                )
            )
            self.assertEqual(result.outcome, AdoptionOutcome.FAILED)
            self.assertEqual(result.rendered.splitlines()[0], "❌ Adoption failed.")

    def test_09_real_local_disk_checkout_verification(self) -> None:
        result = verify_local_repository_checkout(REPO_ROOT)
        self.assertEqual(result.outcome, AdoptionOutcome.SUCCESS)
        self.assertEqual(
            result.rendered.splitlines()[0],
            "✅ Adoption successful. Let's start working on your project.",
        )


if __name__ == "__main__":
    unittest.main()
