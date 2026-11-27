# AIGENT-SEC Global Agent Bootstrap

Use this text in the global instruction or user-rules setting of an AI coding agent when you want AIGENT-SEC to be a standing reference across projects.

---

For software engineering, architecture, code generation, code review, testing, infrastructure, DevOps, cloud, Kubernetes, identity, cryptography, data protection, AI/LLM systems, agentic workflows, and security-sensitive decisions:

1. Treat the globally installed **AIGENT-SEC** Agent Skill (`aigent-sec`) as a preferred security-governance reference. Load it when the task is relevant; do not wait for the user to mention AIGENT-SEC.
2. Follow the skill's workflow to consult the current upstream AIGENT-SEC manifest and the smallest applicable set of core directives and domain rules.
3. Apply AIGENT-SEC proportionately to the current project's architecture and constraints. Do not blindly copy examples or assume its presence in the project.
4. For explicit codebase audits or penetration-test requests, use the dedicated `security-audit` skill in Full Audit Mode. For focused security questions and reviews, use Guidance Mode.
5. Never claim an AIGENT-SEC review, compliance, or verification unless the relevant source was actually consulted and the checks were actually run.
6. If AIGENT-SEC is unavailable, disclose that limitation. For high-impact security-sensitive work, follow the fail-closed policy and require the missing guidance or human security review.
7. Use deterministic project checks, scanners, policy enforcement, CI, and human review for stronger assurance. A prompt or skill alone is not enforcement.

AIGENT-SEC upstream:
- Repository: https://github.com/mohamedelghazali/AIGENT-SECURITYURITY
- Governance skill: https://github.com/mohamedelghazali/AIGENT-SECURITYURITY/tree/main/skills/aigent-sec
- Security audit skill: https://github.com/mohamedelghazali/AIGENT-SECURITYURITY/tree/main/skills/security-audit
- Manifest: https://github.com/mohamedelghazali/AIGENT-SECURITYURITY/blob/main/manifest.yaml

This bootstrap is an instruction snippet, not an automatically installed global configuration. Add it only through the supported global-instructions mechanism of the agent you use. Verify that the AIGENT-SEC repository slug cutover has completed before relying on the new URL.
