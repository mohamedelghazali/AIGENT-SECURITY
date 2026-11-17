#!/usr/bin/env python3
"""Build unified llms-full.txt agent bundle with SHA-256 checksum."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "llms-full.txt"

SOURCE_FILES = [
    "VERSION",
    "AGENTS.md",
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
    "manifest.yaml",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_bundle(root: Path = ROOT, output_file: Path = OUTPUT_FILE) -> str:
    version_path = root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"

    sections: list[str] = []
    file_hashes: list[str] = []

    for rel_path in SOURCE_FILES:
        file_path = root / rel_path
        if not file_path.is_file():
            raise FileNotFoundError(f"Required source file not found: {rel_path}")
        content = file_path.read_text(encoding="utf-8").rstrip("\n")
        file_hash = sha256_text(content + "\n")
        file_hashes.append(f"- {rel_path}: {file_hash}")
        sections.append(
            f"<!-- BEGIN {rel_path} (sha256:{file_hash}) -->\n"
            f"# File: {rel_path}\n\n"
            f"{content}\n"
            f"<!-- END {rel_path} -->"
        )

    body = "\n\n".join(sections) + "\n"
    bundle_sha256 = sha256_text(body)

    header = "\n".join(
        [
            f"# TSAR Agent Governance Bundle (v{version})",
            f"# Bundle SHA-256: {bundle_sha256}",
            "# Source files:",
            *[f"#   {item}" for item in file_hashes],
            "",
            "---",
            "",
        ]
    )

    full_text = header + body
    output_file.write_text(full_text, encoding="utf-8")
    return bundle_sha256


def main() -> int:
    digest = build_bundle()
    print(f"Generated {OUTPUT_FILE.name} (sha256:{digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
