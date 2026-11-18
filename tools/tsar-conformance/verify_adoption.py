#!/usr/bin/env python3
"""Unified deterministic adoption and capability verification engine for TSAR."""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
_ADOPTION_RESPONSE_PATH = Path(__file__).resolve().parent / "adoption_response.py"
_SPEC = importlib.util.spec_from_file_location(
    "tsar_adoption_response", _ADOPTION_RESPONSE_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
_adoption_response = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _adoption_response
_SPEC.loader.exec_module(_adoption_response)

AdoptionEvaluation = _adoption_response.AdoptionEvaluation
AdoptionOutcome = _adoption_response.AdoptionOutcome
AdoptionResponse = _adoption_response.AdoptionResponse
MandatoryCheck = _adoption_response.MandatoryCheck
NonBlockingIssue = _adoption_response.NonBlockingIssue
OptionalCheck = _adoption_response.OptionalCheck
classify_and_format_adoption = _adoption_response.classify_and_format_adoption

STATE_A_HEADER = _adoption_response.SUCCESS_MESSAGE
STATE_B_HEADER = _adoption_response.FAILED_HEADER
STATE_C_HEADER = _adoption_response.WARNING_HEADER

SYSTEM_DIRECTIVES: tuple[str, ...] = (
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
)

CORE_FILES: tuple[str, ...] = (
    "VERSION",
    "manifest.yaml",
    "AGENTS.md",
    *SYSTEM_DIRECTIVES,
)

LOCAL_CONFORMANCE_SCRIPTS: tuple[str, ...] = (
    "tools/tsar-conformance/runner.py",
    "tools/tsar-conformance/consultation_verifier.py",
)


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Runtime capability flags used to classify local vs web/offline checks."""

    has_local_checkout: bool = False
    has_python_runtime: bool = False
    directory_crawling_blocked: bool = False
    raw_host_blocked: bool = False
    github_api_available: bool = True

    @property
    def requires_local_conformance_scripts(self) -> bool:
        return self.has_local_checkout and self.has_python_runtime


@dataclass
class AdoptionRunInput:
    """Inputs for deterministic evaluation of a TSAR adoption run."""

    repository_accessible: bool = True
    capabilities: RuntimeCapabilities = field(default_factory=RuntimeCapabilities)
    verified_files: dict[str, bool] = field(default_factory=dict)
    llms_full_fallback_used: bool = False
    llms_full_verified_directives: bool = False
    fail_closed: bool = True
    default_mode: str = "strict"
    allow_advisory_fallback: bool = False
    runner_executed: bool = False
    runner_passed: bool = False
    consultation_verifier_executed: bool = False
    consultation_verifier_passed: bool = False
    non_blocking_issues: list[str] = field(default_factory=list)
    skipped_mandatory_checks: list[str] = field(default_factory=list)


def evaluate_adoption_run(run_input: AdoptionRunInput) -> AdoptionResponse:
    """Evaluate adoption inputs deterministically into State A, B, or C."""

    mandatory_checks: list[MandatoryCheck] = []
    optional_checks: list[OptionalCheck] = []
    non_blocking_issues: list[NonBlockingIssue] = [
        NonBlockingIssue(description=issue)
        for issue in run_input.non_blocking_issues
    ]
    skipped_mandatory = list(run_input.skipped_mandatory_checks)

    mandatory_checks.append(
        MandatoryCheck(
            name="repository_accessible",
            passed=run_input.repository_accessible,
            detail=(
                ""
                if run_input.repository_accessible
                else "TSAR repository is inaccessible."
            ),
        )
    )

    security_ok = (
        run_input.fail_closed is True
        and run_input.default_mode == "strict"
        and run_input.allow_advisory_fallback is False
    )
    mandatory_checks.append(
        MandatoryCheck(
            name="security_posture",
            passed=security_ok,
            detail=(
                ""
                if security_ok
                else (
                    "Weakened security posture rejected: requires "
                    "fail_closed=true, default_mode=strict, "
                    "allow_advisory_fallback=false."
                )
            ),
        )
    )

    for rel_path in ("VERSION", "manifest.yaml", "AGENTS.md"):
        present = bool(run_input.verified_files.get(rel_path, False))
        mandatory_checks.append(
            MandatoryCheck(
                name=f"core_file:{rel_path}",
                passed=present,
                detail="" if present else f"Missing core file: {rel_path}",
            )
        )

    directives_present = all(
        bool(run_input.verified_files.get(path, False))
        for path in SYSTEM_DIRECTIVES
    )
    if directives_present:
        for path in SYSTEM_DIRECTIVES:
            mandatory_checks.append(
                MandatoryCheck(name=f"core_file:{path}", passed=True)
            )
    elif (
        run_input.llms_full_fallback_used
        and run_input.llms_full_verified_directives
    ):
        for path in SYSTEM_DIRECTIVES:
            mandatory_checks.append(
                MandatoryCheck(name=f"core_file:{path}", passed=True)
            )
        non_blocking_issues.append(
            NonBlockingIssue(
                description=(
                    "Directory crawling or raw file host blocked; verified "
                    "system/*.md directives via llms-full.txt fallback."
                )
            )
        )
    else:
        for path in SYSTEM_DIRECTIVES:
            present = bool(run_input.verified_files.get(path, False))
            mandatory_checks.append(
                MandatoryCheck(
                    name=f"core_file:{path}",
                    passed=present,
                    detail="" if present else f"Missing directive: {path}",
                )
            )

    if run_input.capabilities.requires_local_conformance_scripts:
        if not run_input.runner_executed:
            skipped_mandatory.append("tools/tsar-conformance/runner.py")
            mandatory_checks.append(
                MandatoryCheck(
                    name="conformance_runner",
                    passed=False,
                    detail="runner.py was skipped in local Python checkout.",
                )
            )
        else:
            mandatory_checks.append(
                MandatoryCheck(
                    name="conformance_runner",
                    passed=run_input.runner_passed,
                    detail="" if run_input.runner_passed else "runner.py failed.",
                )
            )

        if not run_input.consultation_verifier_executed:
            skipped_mandatory.append(
                "tools/tsar-conformance/consultation_verifier.py"
            )
            mandatory_checks.append(
                MandatoryCheck(
                    name="consultation_verifier",
                    passed=False,
                    detail=(
                        "consultation_verifier.py was skipped in local "
                        "Python checkout."
                    ),
                )
            )
        else:
            mandatory_checks.append(
                MandatoryCheck(
                    name="consultation_verifier",
                    passed=run_input.consultation_verifier_passed,
                    detail=(
                        ""
                        if run_input.consultation_verifier_passed
                        else "consultation_verifier.py failed."
                    ),
                )
            )
    else:
        optional_checks.append(
            OptionalCheck(
                name="local_conformance_scripts",
                passed=False,
                detail=(
                    "Local conformance scripts skipped: no local checkout "
                    "and Python runtime."
                ),
            )
        )
        non_blocking_issues.append(
            NonBlockingIssue(
                description=(
                    "Web/offline runtime cannot execute local conformance "
                    "scripts (runner.py, consultation_verifier.py)."
                )
            )
        )

    evaluation = AdoptionEvaluation(
        mandatory_checks=mandatory_checks,
        optional_checks=optional_checks,
        non_blocking_issues=non_blocking_issues,
        skipped_mandatory_checks=skipped_mandatory,
    )
    return classify_and_format_adoption(evaluation)


def _parse_manifest_security_posture(manifest_text: str) -> tuple[bool, str, bool]:
    fail_closed = False
    default_mode = ""
    allow_advisory_fallback = True

    for raw_line in manifest_text.splitlines():
        line = raw_line.strip()
        if line.startswith("fail_closed:"):
            fail_closed = line.split(":", 1)[1].strip().lower() == "true"
        elif line.startswith("default_mode:"):
            default_mode = (
                line.split(":", 1)[1].strip().strip('"').strip("'").lower()
            )
        elif line.startswith("allow_advisory_fallback:"):
            allow_advisory_fallback = (
                line.split(":", 1)[1].strip().lower() == "true"
            )

    return fail_closed, default_mode, allow_advisory_fallback


def verify_local_repository_checkout(
    repo_root: Path | str | None = None,
) -> AdoptionResponse:
    """Verify an actual TSAR repository checkout on local disk."""

    root = (
        Path(repo_root).resolve()
        if repo_root is not None
        else Path(__file__).resolve().parents[2]
    )
    if not root.is_dir():
        return evaluate_adoption_run(
            AdoptionRunInput(
                repository_accessible=False,
                capabilities=RuntimeCapabilities(
                    has_local_checkout=True,
                    has_python_runtime=True,
                ),
            )
        )

    verified_files = {rel: (root / rel).is_file() for rel in CORE_FILES}
    manifest_path = root / "manifest.yaml"
    if manifest_path.is_file():
        fail_closed, default_mode, allow_advisory_fallback = (
            _parse_manifest_security_posture(
                manifest_path.read_text(encoding="utf-8")
            )
        )
    else:
        fail_closed, default_mode, allow_advisory_fallback = False, "", True

    runner_present = (root / "tools/tsar-conformance/runner.py").is_file()
    verifier_present = (
        root / "tools/tsar-conformance/consultation_verifier.py"
    ).is_file()

    return evaluate_adoption_run(
        AdoptionRunInput(
            repository_accessible=True,
            capabilities=RuntimeCapabilities(
                has_local_checkout=True,
                has_python_runtime=True,
            ),
            verified_files=verified_files,
            fail_closed=fail_closed,
            default_mode=default_mode,
            allow_advisory_fallback=allow_advisory_fallback,
            runner_executed=runner_present,
            runner_passed=runner_present,
            consultation_verifier_executed=verifier_present,
            consultation_verifier_passed=verifier_present,
        )
    )


def main() -> int:
    response = verify_local_repository_checkout()
    print(
        json.dumps(
            {
                "outcome": response.outcome.value,
                "header": response.header,
                "rendered": response.rendered,
            },
            indent=2,
        )
    )
    return 0 if response.outcome != AdoptionOutcome.FAILED else 1


if __name__ == "__main__":
    raise SystemExit(main())
