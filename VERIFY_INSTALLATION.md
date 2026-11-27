# Verify AIGENT-SEC Installation

Use these checks after installation. Record actual output; do not infer success from a completed command alone.

## 1. Discover skills published by AIGENT-SEC

After the repository slug cutover:

```bash
npx skills add mohamedelghazali/AIGENT-SECURITY --list
```

Before the slug cutover, substitute the current source slug `mohamedelghazali/AIGENT-SECURITYURITY`.

Expected skill names:

- `aigent-sec`
- `crypto-inventory`
- `secret-scanner`
- `secure-review`
- `threat-modeler`
- `security-audit`

Each `SKILL.md` must begin with YAML frontmatter containing both `name` and `description`. The `name` must match its parent directory. The `security-audit` package must also retain all linked companion references, `report-schema.json`, both validators, both validator test suites, and its upstream MIT license.

## 2. Install globally

```bash
npx skills add mohamedelghazali/AIGENT-SECURITY -g --all
```

Review the CLI summary for installed agents, unsupported targets, and the actual installation scope. Use the current legacy repository slug until the GitHub rename is complete.

## 3. Verify installed skills

```bash
npx skills ls -g
```

Confirm that the expected skills are listed for the compatible agents in the output. The exact agent-specific links or directories vary by CLI version and agent.

## 4. Check updates

```bash
npx skills check
npx skills update -g
```

## 5. Smoke-test behavior

Ask the agent to review a small sample for one relevant security topic and report:
- Which AIGENT-SEC skill it loaded.
- Which manifest and rule files it consulted.
- Which checks it actually ran.
- Which checks it could not run.

For an explicit full codebase audit, verify that the dedicated security-audit skill follows its Full Audit Mode workflow and required sandbox boundary.

A smoke test verifies discovery and workflow invocation only. It is not proof of complete security coverage or compliance.

## 6. Persistence test

Start a new project or session with the same agent and verify that the installed skill is still discoverable. If the agent does not load it automatically, configure [AGENT_BOOTSTRAP.md](AGENT_BOOTSTRAP.md) through its documented global-instructions mechanism, if available.

Do not claim universal always-on behavior. Agents differ in their skill discovery and persistence capabilities.
