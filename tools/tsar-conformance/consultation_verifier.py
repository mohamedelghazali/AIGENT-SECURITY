"""Verify real TSAR file consultation via SHA-256 digests and reject unverified claims."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

REQUIRED_CONSULTATION_FILES = (
    "VERSION",
    "manifest.yaml",
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
)

_FORBIDDEN_CLAIM_PATTERNS = (
    re.compile(r"\bllm[- ]only\b", re.IGNORECASE),
    re.compile(r"\bfrom memory\b", re.IGNORECASE),
    re.compile(r"\bwithout reading\b", re.IGNORECASE),
    re.compile(r"\bunexecuted\b", re.IGNORECASE),
    re.compile(r"\bassumed pass(?:ing|ed)?\b", re.IGNORECASE),
    re.compile(r"\bnot actually run\b", re.IGNORECASE),
)


@dataclass
class ConsultationVerificationResult:
    verified: bool
    expected_digests: Dict[str, str] = field(default_factory=dict)
    missing_files: List[str] = field(default_factory=list)
    mismatched_files: List[str] = field(default_factory=list)
    rejected_reasons: List[str] = field(default_factory=list)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_expected_digests(repo_root: Path) -> Dict[str, str]:
    root = Path(repo_root).resolve()
    digests: Dict[str, str] = {}
    for rel in REQUIRED_CONSULTATION_FILES:
        target = root / rel
        if not target.is_file():
            raise FileNotFoundError(f"Required TSAR consultation file missing: {target}")
        digests[rel] = sha256_file(target)
    return digests


def verify_consultation(
    repo_root: Path,
    reported_digests: Optional[Dict[str, str]] = None,
    *,
    llm_only_summary: bool = False,
    unexecuted_claims: Optional[List[str]] = None,
    claim_text: str = "",
) -> ConsultationVerificationResult:
    expected = compute_expected_digests(repo_root)
    missing: List[str] = []
    mismatched: List[str] = []
    reasons: List[str] = []

    if llm_only_summary:
        reasons.append("LLM-only summary rejected: real TSAR file consultation is required.")

    if unexecuted_claims:
        reasons.append(
            f"Unexecuted check claims rejected: {', '.join(str(c) for c in unexecuted_claims)}"
        )

    if claim_text:
        for pattern in _FORBIDDEN_CLAIM_PATTERNS:
            if pattern.search(claim_text):
                reasons.append(
                    f"Disallowed consultation claim pattern matched: {pattern.pattern}"
                )

    provided = reported_digests if isinstance(reported_digests, dict) else None
    if provided is None:
        missing.extend(REQUIRED_CONSULTATION_FILES)
        reasons.append("Missing SHA-256 consultation digests.")
    else:
        for rel in REQUIRED_CONSULTATION_FILES:
            digest = provided.get(rel)
            if not digest:
                missing.append(rel)
            elif str(digest).strip().lower() != expected[rel]:
                mismatched.append(rel)

    if missing:
        reasons.append(f"Missing digests for: {', '.join(missing)}")
    if mismatched:
        reasons.append(f"SHA-256 digest mismatch for: {', '.join(mismatched)}")

    verified = not reasons and not missing and not mismatched
    return ConsultationVerificationResult(
        verified=verified,
        expected_digests=expected,
        missing_files=missing,
        mismatched_files=mismatched,
        rejected_reasons=reasons,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Verify real TSAR file consultation via SHA-256")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--evidence", type=Path, default=None)
    parser.add_argument("--print-expected", action="store_true")
    args = parser.parse_args(argv)

    if args.print_expected:
        print(json.dumps(compute_expected_digests(args.repo_root), indent=2))
        return 0

    if args.evidence is None:
        result = verify_consultation(args.repo_root, None)
    else:
        data = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = verify_consultation(
            args.repo_root,
            data.get("digests"),
            llm_only_summary=bool(data.get("llm_only_summary", False)),
            unexecuted_claims=data.get("unexecuted_claims"),
            claim_text=str(data.get("claim_text", "")),
        )

    print(
        json.dumps(
            {
                "verified": result.verified,
                "missing_files": result.missing_files,
                "mismatched_files": result.mismatched_files,
                "rejected_reasons": result.rejected_reasons,
            },
            indent=2,
        )
    )
    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
