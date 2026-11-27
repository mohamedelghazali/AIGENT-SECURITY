"""Decoupled Host vs. Agent persistent governance installer for AIGENT-SEC."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

BEGIN_MARKER = "<!-- BEGIN TSAR GOVERNANCE -->"
END_MARKER = "<!-- END TSAR GOVERNANCE -->"
WINDSURF_GLOBAL_LIMIT = 6000
SUPPORTED_AGENTS = (
    "codex",
    "claude",
    "gemini",
    "antigravity",
    "windsurf",
    "cursor",
    "copilot",
)


@dataclass
class InstallResult:
    host_manifest_path: Optional[Path]
    agent_results: Dict[str, List[Path]] = field(default_factory=dict)
    version: str = "1.2.0"


def _resolve_home(home_dir: Optional[Path] = None) -> Path:
    if home_dir is not None:
        return Path(home_dir)
    return Path.home()


def _resolve_claude_dir(home: Path) -> Path:
    override = os.environ.get("CLAUDE_CONFIG_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return home / ".claude"


def _read_version(repo_root: Path) -> str:
    version_file = repo_root / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip() or "1.2.0"
    return "1.2.0"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _governance_block(repo_root: Path, version: str, compact: bool = False) -> str:
    if compact:
        body = (
            f"# AIGENT-SEC Security Governance (v{version})\n"
            "Enforce Strict / Warn / Advisory (allow_advisory_fallback: false).\n"
            f"Consult real files in {repo_root}: VERSION, manifest.yaml, "
            "system/CORE_DIRECTIVE.md, system/DO_NOT_GENERATE.md, "
            "system/ENFORCEMENT_LEVELS.md, system/LIFECYCLE.md.\n"
            "Skills: skills/aigent-sec/SKILL.md, python skills/crypto-inventory/inventory.py, "
            "python skills/secret-scanner/scanner.py, python skills/secure-review/review.py, "
            "python skills/threat-modeler/model.py.\n"
            "Never fabricate unexecuted checks or LLM-only consultation summaries."
        )
    else:
        body = (
            f"# AIGENT-SEC Security Governance (v{version})\n\n"
            "- Enforcement Levels: Strict / Warn / Advisory (`allow_advisory_fallback: false`, fail-closed).\n"
            f"- Mandatory Consultation Root: `{repo_root}`\n"
            "- Consult real files before security-sensitive work: `VERSION`, `manifest.yaml`, "
            "`system/CORE_DIRECTIVE.md`, `system/DO_NOT_GENERATE.md`, "
            "`system/ENFORCEMENT_LEVELS.md`, `system/LIFECYCLE.md`.\n"
            "- Skill Entry Points: `skills/aigent-sec/SKILL.md`, "
            "`python skills/crypto-inventory/inventory.py`, "
            "`python skills/secret-scanner/scanner.py`, "
            "`python skills/secure-review/review.py`, "
            "`python skills/threat-modeler/model.py`.\n"
            "- Truthful Reporting: Never claim unexecuted checks or LLM-only summaries as file consultation."
        )
    return f"{BEGIN_MARKER}\n{body}\n{END_MARKER}"


def upsert_marked_section(
    path: Path,
    block: str,
    max_chars: Optional[int] = None,
    compact_block: Optional[str] = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""

    def _merge(content: str, section: str) -> str:
        if BEGIN_MARKER in content and END_MARKER in content:
            start = content.index(BEGIN_MARKER)
            end = content.index(END_MARKER, start) + len(END_MARKER)
            before = content[:start].rstrip("\n")
            after = content[end:].lstrip("\n")
            parts = [p for p in (before, section, after) if p]
            return "\n\n".join(parts) + "\n"
        stripped = content.rstrip("\n")
        if stripped:
            return f"{stripped}\n\n{section}\n"
        return f"{section}\n"

    updated = _merge(existing, block)
    if max_chars is not None and len(updated) > max_chars:
        if compact_block is not None:
            updated = _merge(existing, compact_block)
        if len(updated) > max_chars:
            minimal = f"{BEGIN_MARKER}\nAIGENT-SEC v1.2.0 Strict/Warn/Advisory (allow_advisory_fallback: false).\n{END_MARKER}"
            updated = _merge(existing, minimal)
        if len(updated) > max_chars:
            raise ValueError(f"{path} exceeds {max_chars} char limit ({len(updated)} chars)")

    path.write_text(updated, encoding="utf-8")
    return path


def _install_skills(skill_dirs: List[Path], repo_root: Path, version: str) -> List[Path]:
    written: List[Path] = []
    block = _governance_block(repo_root, version, compact=False)
    for skill_dir in skill_dirs:
        tsar_skill = skill_dir / "aigent-sec" / "SKILL.md"
        written.append(upsert_marked_section(tsar_skill, block))
    return written


def install_host(repo_root: Path, home_dir: Optional[Path] = None) -> Path:
    repo_root = Path(repo_root).resolve()
    home = _resolve_home(home_dir)
    version = _read_version(repo_root)
    host_path = home / ".tsar" / "host-installation.json"
    host_path.parent.mkdir(parents=True, exist_ok=True)

    core_rel_paths = [
        "VERSION",
        "manifest.yaml",
        "system/CORE_DIRECTIVE.md",
        "system/DO_NOT_GENERATE.md",
        "system/ENFORCEMENT_LEVELS.md",
        "system/LIFECYCLE.md",
    ]
    digests: Dict[str, str] = {}
    for rel in core_rel_paths:
        target = repo_root / rel
        if target.is_file():
            digests[rel] = _sha256_file(target)

    payload = {
        "schema": "tsar-host-installation/v1",
        "version": version,
        "repo_root": str(repo_root),
        "decoupled": True,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "core_digests": digests,
    }
    host_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return host_path


def install_agent(
    agent: str,
    repo_root: Path,
    project_root: Optional[Path] = None,
    home_dir: Optional[Path] = None,
) -> List[Path]:
    name = agent.strip().lower()
    if name == "devin":
        name = "windsurf"
    if name not in SUPPORTED_AGENTS:
        raise ValueError(f"Unsupported agent: {agent}")

    repo_root = Path(repo_root).resolve()
    proj = Path(project_root).resolve() if project_root is not None else repo_root
    home = _resolve_home(home_dir)
    version = _read_version(repo_root)
    block = _governance_block(repo_root, version, compact=False)
    compact = _governance_block(repo_root, version, compact=True)
    written: List[Path] = []

    if name == "codex":
        written.append(upsert_marked_section(home / ".codex" / "AGENTS.md", block))
        written.extend(_install_skills([home / ".agents" / "skills"], repo_root, version))
    elif name == "claude":
        claude_dir = _resolve_claude_dir(home)
        written.append(upsert_marked_section(claude_dir / "CLAUDE.md", block))
        written.extend(_install_skills([claude_dir / "skills"], repo_root, version))
    elif name == "gemini":
        written.append(upsert_marked_section(home / ".gemini" / "GEMINI.md", block))
        written.extend(_install_skills([home / ".agents" / "skills"], repo_root, version))
    elif name == "antigravity":
        written.append(upsert_marked_section(home / ".gemini" / "GEMINI.md", block))
        written.extend(
            _install_skills(
                [home / ".gemini" / "config" / "skills", home / ".agents" / "skills"],
                repo_root,
                version,
            )
        )
    elif name == "windsurf":
        global_rules = home / ".codeium" / "windsurf" / "memories" / "global_rules.md"
        written.append(
            upsert_marked_section(
                global_rules,
                compact,
                max_chars=WINDSURF_GLOBAL_LIMIT,
                compact_block=compact,
            )
        )
        written.append(upsert_marked_section(proj / ".devin" / "rules" / "aigent-sec.md", block))
        written.append(upsert_marked_section(proj / ".windsurf" / "rules" / "aigent-sec.md", block))
    elif name == "cursor":
        mdc_block = (
            "---\n"
            "description: AIGENT-SEC Universal Security Governance\n"
            "alwaysApply: true\n"
            "---\n\n"
            f"{block}"
        )
        written.append(upsert_marked_section(proj / ".cursor" / "rules" / "aigent-sec.mdc", mdc_block))
        written.extend(_install_skills([home / ".agents" / "skills"], repo_root, version))
    elif name == "copilot":
        written.append(
            upsert_marked_section(proj / ".github" / "copilot-instructions.md", block)
        )
        written.extend(_install_skills([home / ".agents" / "skills"], repo_root, version))

    return written


def install_all(
    repo_root: Path,
    project_root: Optional[Path] = None,
    home_dir: Optional[Path] = None,
    agents: Optional[List[str]] = None,
    include_host: bool = True,
) -> InstallResult:
    version = _read_version(Path(repo_root).resolve())
    host_path = install_host(repo_root, home_dir=home_dir) if include_host else None
    selected = list(agents) if agents is not None else list(SUPPORTED_AGENTS)
    results: Dict[str, List[Path]] = {}
    for agent in selected:
        results[agent] = install_agent(
            agent,
            repo_root=repo_root,
            project_root=project_root,
            home_dir=home_dir,
        )
    return InstallResult(host_manifest_path=host_path, agent_results=results, version=version)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AIGENT-SEC decoupled host/agent universal installer")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--home", type=Path, default=None)
    parser.add_argument("--host-only", action="store_true")
    parser.add_argument("--agent", action="append", dest="agents")
    args = parser.parse_args(argv)

    if args.host_only:
        install_host(args.repo_root, home_dir=args.home)
        return 0

    install_all(
        repo_root=args.repo_root,
        project_root=args.project_root,
        home_dir=args.home,
        agents=args.agents,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
