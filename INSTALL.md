# Install AIGENT-SEC

## Recommended global installation

Install all valid skills from the canonical AIGENT-SECURITY repository globally for detected compatible agents:

```bash
npx skills add mohamedelghazali/AIGENT-SECURITY -g --all
```

## Published skills

AIGENT-SEC provides six Agent Skills packages:

- `aigent-sec` — primary governance skill and navigation entry point.
- `crypto-inventory` — cryptographic inventory workflow.
- `secret-scanner` — hardcoded-secret detection workflow.
- `secure-review` — static application-security review workflow.
- `threat-modeler` — STRIDE threat-model generation workflow.
- `security-audit` — Cloudflare-derived adversarial security audit workflow, including its complete companion files and validators.

Each skill's `SKILL.md` must contain valid YAML frontmatter with both `name` and `description`; the `name` must match its directory.

## Verify

```bash
npx skills ls -g
npx skills check
```

Confirm that the expected skills appear for compatible agents and review the CLI output for unsupported targets.

## Update

```bash
npx skills update -g
```

Updates are explicit; do not assume an installed skill is live-synchronized with GitHub.

## No shell or no global-skill support?

Read [`ONBOARDING.md`](ONBOARDING.md) and [Universal Agent Onboarding](docs/universal-agent-onboarding.md). Retrieve the core directives and applicable rules for the current task, and report honestly that persistent installation was unavailable. Do not invent settings paths or silently modify unrelated configuration.

Global installation makes skills discoverable to compatible agents under the installing user account. It does not force a skill to activate on every turn, modify model training, or provide deterministic enforcement. Use the agent's documented global-instructions mechanism for additional standing behavior.

See the [Vercel Skills CLI documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for current command behavior and supported agents.
