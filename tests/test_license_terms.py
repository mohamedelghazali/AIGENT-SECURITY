"""Governance tests for TSAR licensing and contributor guidance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_license_reserves_commercial_use_and_preserves_prior_grants():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
     assert "MIT License" in license_text
    assert "Copyright (c) 2026 Mohamed El Ghazali" in license_text
    assert "Permission is hereby granted, free of charge" in license_text
    assert "Telephone: +213 541436814" in license_text



def test_contribution_guidance_references_license_grant():
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "Contributor Licensing" in contributing
    assert "retain copyright ownership" in contributing
    assert "LICENSE" in contributing


def test_sync_documentation_does_not_claim_automatic_rule_rewrites():
    faq = (ROOT / "docs" / "faq-extended.md").read_text(encoding="utf-8")
    assert "does not automatically rewrite TSAR rule text" in faq
