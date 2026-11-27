"""Integrity and packaging tests for the imported Cloudflare security-audit skill."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

EXPECTED_SKILLS = {
    "aigent-sec",
    "crypto-inventory",
    "secret-scanner",
    "secure-review",
    "threat-modeler",
    "security-audit",
}

CLOUDFLARE_FILES = {
    "SKILL.md",
    "RECONNAISSANCE.md",
    "HUNTING.md",
    "ATTACK-CLASSES.md",
    "AI-AND-LLM.md",
    "CLIENT-SIDE.md",
    "MEMORY-SAFETY-AND-BINARY.md",
    "WEB-PROTOCOL-AND-AUTH.md",
    "SUPPLY-CHAIN-AND-RELEASE.md",
    "CLOUD-AND-DEPLOYMENT.md",
    "PROTOCOLS-RPC-AND-MESSAGING.md",
    "RESOURCE-EXHAUSTION-AND-AVAILABILITY.md",
    "DATA-ISOLATION-AND-LIFECYCLE.md",
    "DESKTOP-MOBILE-AND-LOCAL-IPC.md",
    "VALIDATION-AND-REPORTING.md",
    "report-schema.json",
    "validate-findings.cjs",
    "validate-findings.test.cjs",
    "validate-coverage-ledger.cjs",
    "validate-coverage-ledger.test.cjs",
}


def _skill_frontmatter(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_dir.name} SKILL.md has no YAML frontmatter"
    _, frontmatter, _ = text.split("---", 2)
    data = yaml.safe_load(frontmatter)
    assert isinstance(data, dict), f"{skill_dir.name} frontmatter is not a mapping"
    assert isinstance(data.get("name"), str) and data["name"].strip()
    assert isinstance(data.get("description"), str) and data["description"].strip()
    return data


def test_all_published_skills_have_valid_frontmatter() -> None:
    actual = {p.name for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}
    assert EXPECTED_SKILLS <= actual
    for name in EXPECTED_SKILLS:
        assert _skill_frontmatter(SKILLS / name)["name"] == name


def test_cloudflare_package_is_complete_and_self_contained() -> None:
    skill_dir = SKILLS / "security-audit"
    actual = {p.name for p in skill_dir.iterdir() if p.is_file()}
    assert CLOUDFLARE_FILES <= actual
    assert len(CLOUDFLARE_FILES) == 20

    schema = json.loads((skill_dir / "report-schema.json").read_text(encoding="utf-8"))
    assert isinstance(schema, dict)
    assert (skill_dir / "LICENSE").is_file()
    license_text = (skill_dir / "LICENSE").read_text(encoding="utf-8")
    assert "MIT License" in license_text
    assert "Copyright (c) 2025-2026 Cloudflare, Inc." in license_text
    assert (skill_dir / "UPSTREAM-README.md").is_file()


def test_cloudflare_upstream_attribution_is_recorded() -> None:
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "cloudflare/security-audit-skill" in notice
    assert "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8" in notice
    assert "MIT" in notice


def test_primary_aigent_sec_skill_is_the_canonical_agent_entrypoint() -> None:
    primary = _skill_frontmatter(SKILLS / "aigent-sec")
    assert primary["name"] == "aigent-sec"
    assert "AIGENT-SEC" in (SKILLS / "aigent-sec" / "SKILL.md").read_text(encoding="utf-8")
