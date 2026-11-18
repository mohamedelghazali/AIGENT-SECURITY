"""Regression tests for decoupled TSAR host/agent adoption and consultation verification."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, rel_path: str):
    path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = _load_module("universal_installer", "tools/tsar-installer/universal_installer.py")
verifier = _load_module("consultation_verifier", "tools/tsar-conformance/consultation_verifier.py")


class TestUniversalAdoption(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.project_a = self.root / "project_a"
        self.project_b = self.root / "project_b"
        self.project_a.mkdir(parents=True, exist_ok=True)
        self.project_b.mkdir(parents=True, exist_ok=True)

    def test_host_and_agent_decoupling(self) -> None:
        host_manifest = installer.install_host(REPO_ROOT, home_dir=self.home)
        self.assertEqual(host_manifest, self.home / ".tsar" / "host-installation.json")
        self.assertTrue(host_manifest.is_file())
        data = json.loads(host_manifest.read_text(encoding="utf-8"))
        self.assertTrue(data["decoupled"])
        self.assertIn("VERSION", data["core_digests"])
        self.assertFalse((self.home / ".codex" / "AGENTS.md").exists())
        self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())

        installer.install_agent("codex", REPO_ROOT, project_root=self.project_a, home_dir=self.home)
        self.assertTrue((self.home / ".codex" / "AGENTS.md").is_file())

    def test_all_seven_agent_adapters(self) -> None:
        old_env = os.environ.pop("CLAUDE_CONFIG_DIR", None)
        try:
            result = installer.install_all(
                REPO_ROOT, project_root=self.project_a, home_dir=self.home
            )
            self.assertEqual(set(result.agent_results.keys()), set(installer.SUPPORTED_AGENTS))

            expected_files = [
                self.home / ".tsar" / "host-installation.json",
                self.home / ".codex" / "AGENTS.md",
                self.home / ".agents" / "skills" / "tsar" / "SKILL.md",
                self.home / ".claude" / "CLAUDE.md",
                self.home / ".claude" / "skills" / "tsar" / "SKILL.md",
                self.home / ".gemini" / "GEMINI.md",
                self.home / ".gemini" / "config" / "skills" / "tsar" / "SKILL.md",
                self.home / ".codeium" / "windsurf" / "memories" / "global_rules.md",
                self.project_a / ".devin" / "rules" / "tsar.md",
                self.project_a / ".windsurf" / "rules" / "tsar.md",
                self.project_a / ".cursor" / "rules" / "tsar.mdc",
                self.project_a / ".github" / "copilot-instructions.md",
            ]
            for path in expected_files:
                self.assertTrue(path.is_file(), f"Missing expected adapter output: {path}")
        finally:
            if old_env is not None:
                os.environ["CLAUDE_CONFIG_DIR"] = old_env

    def test_existing_config_and_skill_preservation(self) -> None:
        codex_file = self.home / ".codex" / "AGENTS.md"
        codex_file.parent.mkdir(parents=True, exist_ok=True)
        codex_file.write_text("# My Custom Codex Rules\nAlways run unit tests.\n", encoding="utf-8")

        custom_skill = self.home / ".agents" / "skills" / "custom-skill" / "SKILL.md"
        custom_skill.parent.mkdir(parents=True, exist_ok=True)
        custom_skill.write_text("# User Custom Skill\nKeep untouched.\n", encoding="utf-8")

        installer.install_agent("codex", REPO_ROOT, project_root=self.project_a, home_dir=self.home)
        content = codex_file.read_text(encoding="utf-8")
        self.assertIn("# My Custom Codex Rules", content)
        self.assertIn(installer.BEGIN_MARKER, content)
        self.assertIn(installer.END_MARKER, content)
        self.assertEqual(
            custom_skill.read_text(encoding="utf-8"),
            "# User Custom Skill\nKeep untouched.\n",
        )

    def test_idempotency(self) -> None:
        installer.install_all(REPO_ROOT, project_root=self.project_a, home_dir=self.home)
        codex_file = self.home / ".codex" / "AGENTS.md"
        first = codex_file.read_text(encoding="utf-8")

        installer.install_all(REPO_ROOT, project_root=self.project_a, home_dir=self.home)
        second = codex_file.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertEqual(second.count(installer.BEGIN_MARKER), 1)
        self.assertEqual(second.count(installer.END_MARKER), 1)

    def test_claude_config_dir_override(self) -> None:
        custom_claude = self.root / "custom_claude_cfg"
        old_env = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(custom_claude)
        try:
            installer.install_agent(
                "claude", REPO_ROOT, project_root=self.project_a, home_dir=self.home
            )
            self.assertTrue((custom_claude / "CLAUDE.md").is_file())
            self.assertTrue((custom_claude / "skills" / "tsar" / "SKILL.md").is_file())
            self.assertFalse((self.home / ".claude" / "CLAUDE.md").exists())
        finally:
            if old_env is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = old_env

    def test_windsurf_char_limit(self) -> None:
        global_rules = self.home / ".codeium" / "windsurf" / "memories" / "global_rules.md"
        global_rules.parent.mkdir(parents=True, exist_ok=True)
        global_rules.write_text("User rule line\n" * 300, encoding="utf-8")

        installer.install_agent(
            "windsurf", REPO_ROOT, project_root=self.project_a, home_dir=self.home
        )
        content = global_rules.read_text(encoding="utf-8")
        self.assertLessEqual(len(content), 6000)
        self.assertIn(installer.BEGIN_MARKER, content)

    def test_cross_project_persistence(self) -> None:
        installer.install_all(REPO_ROOT, project_root=self.project_a, home_dir=self.home)
        installer.install_all(REPO_ROOT, project_root=self.project_b, home_dir=self.home)
        self.assertTrue((self.home / ".codex" / "AGENTS.md").is_file())
        self.assertTrue((self.home / ".gemini" / "GEMINI.md").is_file())
        self.assertTrue((self.project_a / ".cursor" / "rules" / "tsar.mdc").is_file())
        self.assertTrue((self.project_b / ".cursor" / "rules" / "tsar.mdc").is_file())
        self.assertTrue((self.project_a / ".github" / "copilot-instructions.md").is_file())
        self.assertTrue((self.project_b / ".github" / "copilot-instructions.md").is_file())

    def test_real_file_sha256_consultation_verification(self) -> None:
        digests = verifier.compute_expected_digests(REPO_ROOT)
        self.assertEqual(set(digests.keys()), set(verifier.REQUIRED_CONSULTATION_FILES))

        ok = verifier.verify_consultation(REPO_ROOT, digests)
        self.assertTrue(ok.verified)
        self.assertEqual(ok.rejected_reasons, [])

        bad_digests = dict(digests)
        bad_digests["VERSION"] = "0" * 64
        tampered = verifier.verify_consultation(REPO_ROOT, bad_digests)
        self.assertFalse(tampered.verified)
        self.assertIn("VERSION", tampered.mismatched_files)

        llm_only = verifier.verify_consultation(REPO_ROOT, digests, llm_only_summary=True)
        self.assertFalse(llm_only.verified)

        unexecuted = verifier.verify_consultation(
            REPO_ROOT, digests, unexecuted_claims=["secret-scanner"]
        )
        self.assertFalse(unexecuted.verified)

        claimed = verifier.verify_consultation(
            REPO_ROOT, digests, claim_text="Summarized from memory without reading files"
        )
        self.assertFalse(claimed.verified)


if __name__ == "__main__":
    unittest.main()
