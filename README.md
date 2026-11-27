# AIGENT-SEC — AI-Agent Security Engineering & Governance

> **Stop vulnerabilities at the source. Secure every line of AI-generated code.**

**A provider-neutral security engineering governance standard for AI coding agents and AI-assisted software development.**

AIGENT-SEC brings security policy, domain-specific engineering rules, agent integrations, deterministic local checks, repository automation, and adversarial security auditing into one maintainable framework. It is designed to move security decisions earlier in the software lifecycle while keeping implementation claims tied to observable evidence.

## Governance baseline

AIGENT-SEC carries forward the existing v1.2.0 governance baseline. The rebranding and Cloudflare skill integration do not, by themselves, constitute a new release qualification.

| Capability | Current baseline |
|---|---:|
| Active governance files | **175** |
| Domain security rule files | **171** |
| Security rule domains | **37** |
| Core directives | **4** |
| Agent compatibility profiles | **15** |
| Agent Skills packages | **6** (five existing AIGENT-SEC skills plus the integrated security-audit skill) |
| Enforcement defaults | **Strict**, fail-closed |
| Advisory fallback | Disabled |

The authoritative inventory and enforcement settings remain in [`manifest.yaml`](manifest.yaml). The required core directives are:

- `system/CORE_DIRECTIVE.md`
- `system/DO_NOT_GENERATE.md`
- `system/ENFORCEMENT_LEVELS.md`
- `system/LIFECYCLE.md`

The manifest's current security posture is `lifecycle.fail_closed: true`, `enforcement.default_mode: strict`, and `enforcement.allow_advisory_fallback: false`. Missing mandatory policy context is not permission to silently downgrade to Advisory.

## What AIGENT-SEC provides

1. **Provider-neutral governance:** one canonical instruction set, core directives, enforcement levels, and versioned domain rules.
2. **Security knowledge base:** reusable requirements covering application, API, cloud, identity, cryptography, infrastructure, data, privacy, AI/LLM, agentic systems, and supply-chain security.
3. **Agent adoption:** Agent Skills packages, a universal onboarding procedure, and 15 compatibility profiles.
4. **Deterministic tooling:** secret scanning, secure-review heuristics, cryptographic inventory, threat-modeling support, CLI utilities, orchestration, reporting, and repository checks.
5. **Delivery controls:** CI workflows, policy-as-code examples, hooks, validation scripts, and test suites.
6. **Adversarial security auditing:** a dedicated integration of Cloudflare's Security Audit Skill, including its full companion references, structured report schema, validators, and tests.

AIGENT-SEC is not a model, a provider-level system prompt, or a guarantee that an agent will obey instructions. Skills and prompts guide agent behavior; scanners, hooks, CI, protected branches, and independent review provide additional controls.

## Engineering lifecycle

For relevant software engineering and security-sensitive work, apply the framework proportionately through:

`CONSULT → CLASSIFY → DESIGN → IMPLEMENT → SCAN → REVIEW → VERIFY → REPORT`

Resolve the applicable core directives and domain rules before material decisions. Keep untrusted source content and tool output separate from trusted instructions. Use least privilege, fail-closed handling, and independent verification. Report what was actually consulted and executed; never convert an unavailable check into PASS.

## Adversarial security audit

The integrated [`security-audit` skill](skills/security-audit/SKILL.md) retains Cloudflare's upstream implementation and all 20 files in its skill package. It complements rather than replaces AIGENT-SEC's existing scanners.

It provides two operating modes:

- **Guidance mode:** focused security questions, code review, triage, and methodology. Loading the skill alone does not launch a full audit or create report files.
- **Full audit mode:** used for explicit codebase audits, penetration-test requests, comprehensive reviews, or requested report artifacts. It follows the upstream six-phase process: reconnaissance, coverage-led hunting, candidate validation, structured findings, independent record verification, and target-neutral reporting.

The skill distinguishes `confirmed`, `needs_validation`, and `rejected` candidates. Unconfirmed leads do not receive severity. Target-controlled builds and tests require the specified OS-enforced sandbox; if the required isolation cannot be established, execution is blocked and the missing capability must be reported.

The complete imported package is self-contained under `skills/security-audit/`, including `SKILL.md`, companion references, `report-schema.json`, both validators, and both validator test suites. Upstream attribution and the MIT license are preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and `skills/security-audit/LICENSE`.

## Installation

Install all AIGENT-SEC skills globally for detected compatible agents:

```bash
npx skills add mohamedelghazali/AIGENT-SECURITY -g --all
npx skills ls -g
npx skills check
npx skills update -g
```

The Vercel Skills CLI installs valid skills to supported agent locations it detects. Global installation does not force every agent to load a skill on every turn, modify model training, or provide deterministic enforcement. Consult [`INSTALL.md`](INSTALL.md), [`COMPATIBILITY.md`](COMPATIBILITY.md), and [`VERIFY_INSTALLATION.md`](VERIFY_INSTALLATION.md) for scope, compatibility, and verification.

## Direct canonical URLs (for URL-allowlisted runtimes that only fetch explicit URLs):

- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/llms-full.txt
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/VERSION
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/manifest.yaml
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/AGENTS.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/system/CORE_DIRECTIVE.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/system/DO_NOT_GENERATE.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/system/ENFORCEMENT_LEVELS.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/system/LIFECYCLE.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/docs/universal-agent-onboarding.md
- https://raw.githubusercontent.com/mohamedelghazali/AIGENT-SECURITY/main/docs/release-qualification.md
- https://api.github.com/repos/mohamedelghazali/AIGENT-SECURITY/contents/llms-full.txt

## Current-session adoption

For chat-only or restricted environments, provide this prompt to the agent:

```text
Adopt AIGENT-SEC as the security engineering governance standard for this task:
https://github.com/mohamedelghazali/AIGENT-SECURITY

Read the repository's actual AGENTS.md, manifest.yaml, four core directives,
and the smallest applicable set of domain rules. Apply the documented
CONSULT → CLASSIFY → DESIGN → IMPLEMENT → SCAN → REVIEW → VERIFY → REPORT
lifecycle where relevant.

Use the dedicated security-audit skill for explicit codebase audits or
penetration-test requests, following its guidance/full-audit mode boundary.

Verify access and source freshness before relying on the framework. Honor
fail_closed=true, default_mode=strict, and allow_advisory_fallback=false.
Do not claim installation, persistence, consultation, execution, compliance,
or verification without observed evidence. If required policy content or
a mandatory capability is unavailable, report the limitation and stop
security-sensitive implementation where the policy requires it.
Keep AIGENT-SEC active for relevant engineering work throughout this
conversation; do not claim that chat-only adoption persists to future sessions.
```

## Repository map

| Area | Purpose |
|---|---|
| `system/` | Core directives and enforcement model |
| `rules/` and `manifest.yaml` | Domain rules and authoritative inventory |
| `skills/` | Installable skills and scanners |
| `prompts/` and `integrations/` | Universal instructions and agent/CI adapters |
| `tools/` | CLI, installer, conformance, orchestration, reporting, LSP, and dashboard tooling |
| `policies/` | Policy-as-code examples |
| `tests/` and `.github/workflows/` | Automated checks and CI |
| `docs/` | Architecture, adoption, compatibility, operations, and compliance guidance |

Some existing command names, package identifiers, schema namespaces, workflow check names, and tool source paths retain their historical `tsar` identifiers for backward compatibility. They are implementation interfaces, not the public product name; they must not be removed without a compatibility migration and corresponding tests.

## Licensing

The root `LICENSE` governs AIGENT-SEC content. The Cloudflare Security Audit Skill is separately distributed under its upstream MIT license, retained with the imported files. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Verification and contribution

Use `./verify-all.sh` for the documented repository verification entry point when the required dependencies and runtime are available. The integrated Cloudflare validator suites are also run in CI. See [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting changes.

A successful test run proves only the checks that actually ran. It does not certify the absence of vulnerabilities, guarantee agent compliance, or establish production deployment behavior.
