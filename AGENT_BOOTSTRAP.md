# AIGENT-SEC Global Agent Bootstrap

Add this guidance to an agent's documented global instructions or user-rules setting. Do not assume this file is automatically installed or that one configuration file controls every agent.

---

For software engineering, architecture, code generation, code review, testing, infrastructure, DevOps, cloud, Kubernetes, identity, cryptography, data protection, AI/LLM systems, agentic workflows, and security-sensitive decisions:

1. Treat the globally installed **AIGENT-SEC** Agent Skill (`aigent-sec`) as a preferred security-governance reference. Load it when the task is relevant; do not wait for the user to mention it.
2. Consult the current upstream manifest and the smallest applicable set of core directives and domain rules.
3. Apply AIGENT-SEC proportionately to the current project's architecture and constraints. Do not blindly copy examples or assume the framework is installed in the project.
4. For explicit codebase security audits or pen-test requests, use the dedicated `security-audit` skill in Full Audit Mode and follow its sandbox, evidence, and independent-verification requirements. Use Guidance Mode for focused security questions and reviews.
5. Never claim review, compliance, installation, persistence, or verification unless the relevant source was actually consulted and the checks were actually run.
6. If AIGENT-SEC or a required capability is unavailable, disclose that limitation. For high-impact security-sensitive work, stop where the fail-closed policy requires it and request the missing guidance or human security review.
7. Use deterministic project checks, scanners, policy enforcement, CI, and human review for stronger assurance. A prompt or skill alone is not enforcement.

AIGENT-SEC upstream:
- Repository: https://github.com/mohamedelghazali/AIGENT-SECURITY
- Primary skill: skills/aigent-sec/SKILL.md
- Security audit skill: skills/security-audit/SKILL.md
- Manifest: manifest.yaml

The canonical repository slug is `mohamedelghazali/AIGENT-SECURITY`.
