# Install AIGENT-SEC

## Recommended global installation

After the GitHub repository slug is renamed to `AIGENT-SEC`, install all valid skills for all detected compatible agents:

```bash
npx skills add mohamedelghazali/AIGENT-SEC -g --all
```

Until that repository-settings cutover is completed, the existing repository slug is still `mohamedelghazali/TSAR`; use this temporary source:

```bash
npx skills add mohamedelghazali/TSAR -g --all
```

This asks the Vercel Skills CLI to install every valid skill discovered in the repository to all agents it detects, using global scope. Actual support varies by agent; the CLI reports unsupported targets.

## Published skills

AIGENT-SEC provides the following Agent Skills packages:

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
```

Inspect the CLI output and confirm that the six expected skill names appear for the agents and scopes that support them.

## Update

```bash
npx skills check
npx skills update -g
```

Updates are explicit; do not assume an installed skill is live-synchronized with GitHub.

## No shell or no global-skill support?

Read [ONBOARDING.md](ONBOARDING.md) and [Universal Agent Onboarding](docs/universal-agent-onboarding.md). Retrieve the core directives and applicable rules for the current task, and report honestly that persistent installation was unavailable. Do not invent settings paths or silently modify unrelated configuration.

See the [Vercel Skills CLI documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for current command behavior and supported agents.
