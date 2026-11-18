"""Deterministic 3-state TSAR adoption outcome classification and response formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence
SUCCESS_MESSAGE = "✅ Adoption successful. Let's start working on your project."
FAILED_HEADER = "❌ Adoption failed."
WARNING_HEADER = "⚠️ Adoption successful, but some issues require attention."


class AdoptionOutcome(str, Enum):
    """Deterministic outcome states for TSAR adoption."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SUCCESS_WITH_WARNINGS = "SUCCESS_WITH_WARNINGS"


@dataclass(frozen=True)
class MandatoryCheck:
    """Result of a mandatory TSAR adoption check."""

    name: str
    passed: bool = True
    executed: bool = True
    details: str = ""


@dataclass(frozen=True)
class OptionalCheck:
    """Result of an optional TSAR adoption check."""

    name: str
    executed: bool = True
    available: bool = True
    passed: bool = True
    details: str = ""


@dataclass(frozen=True)
class NonBlockingIssue:
    """Non-blocking warning or issue observed during TSAR adoption."""

    summary: str
    impact: str = ""


@dataclass(frozen=True)
class AdoptionEvaluation:
    """Aggregated inputs used to classify a TSAR adoption run."""

    repository_accessible: bool = True
    missing_mandatory_files: Sequence[str] = field(default_factory=tuple)
    mandatory_checks: Sequence[MandatoryCheck] = field(default_factory=tuple)
    optional_checks: Sequence[OptionalCheck] = field(default_factory=tuple)
    non_blocking_issues: Sequence[NonBlockingIssue] = field(default_factory=tuple)
    repository_error: str = ""


@dataclass(frozen=True)
class AdoptionResponse:
    """Classified outcome and formatted final response."""

    outcome: AdoptionOutcome
    message: str
    lines: tuple[str, ...]


def _format_detail(details: str) -> str:
    cleaned = details.strip()
    return f" ({cleaned})" if cleaned else ""


def classify_and_format_adoption(evaluation: AdoptionEvaluation) -> AdoptionResponse:
    """Classify TSAR adoption outcome and format the deterministic response."""
    failure_lines: list[str] = []

    if not evaluation.repository_accessible:
        reason = evaluation.repository_error.strip() or "TSAR repository could not be accessed."
        failure_lines.append(f"- Repository inaccessible: {reason}")

    for missing_file in evaluation.missing_mandatory_files:
        failure_lines.append(f"- Missing mandatory file: {missing_file}")

    if not evaluation.mandatory_checks:
        failure_lines.append("- Mandatory checks missing: no mandatory checks were executed.")

    for check in evaluation.mandatory_checks:
        if not check.executed:
            failure_lines.append(
                f"- Mandatory check not executed: {check.name}{_format_detail(check.details)}"
            )
        elif not check.passed:
            failure_lines.append(
                f"- Mandatory check failed: {check.name}{_format_detail(check.details)}"
            )

    if failure_lines:
        lines = (FAILED_HEADER, *failure_lines)
        return AdoptionResponse(
            outcome=AdoptionOutcome.FAILED,
            message="\n".join(lines),
            lines=lines,
        )

    warning_lines: list[str] = []

    for issue in evaluation.non_blocking_issues:
        impact = issue.impact.strip() or "non-blocking"
        warning_lines.append(f"- Non-blocking issue: {issue.summary} (Impact: {impact})")

    for opt in evaluation.optional_checks:
        if not opt.available:
            warning_lines.append(
                f"- Optional check unavailable: {opt.name}{_format_detail(opt.details)}"
            )
        elif not opt.executed:
            warning_lines.append(
                f"- Optional check not executed: {opt.name}{_format_detail(opt.details)}"
            )
        elif not opt.passed:
            warning_lines.append(
                f"- Optional check failed: {opt.name}{_format_detail(opt.details)}"
            )

    if warning_lines:
        completed_lines = [
            f"- Completed mandatory check: {check.name}" for check in evaluation.mandatory_checks
        ]
        lines = (WARNING_HEADER, *warning_lines, *completed_lines)
        return AdoptionResponse(
            outcome=AdoptionOutcome.SUCCESS_WITH_WARNINGS,
            message="\n".join(lines),
            lines=lines,
        )

    return AdoptionResponse(
        outcome=AdoptionOutcome.SUCCESS,
        message=SUCCESS_MESSAGE,
        lines=(SUCCESS_MESSAGE,),
    )
