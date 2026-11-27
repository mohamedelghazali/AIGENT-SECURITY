# Install AIGENT-SEC as a Global Agent Skill

This guide covers installing AIGENT-SEC once for compatible coding agents. For the one-link adoption workflow, see [Universal Agent Onboarding](universal-agent-onboarding.md).

## Install globally for all detected agents

After the repository slug has been renamed to `AIGENT-SEC`:

```bash
npx skills add mohamedelghazali/AIGENT-SEC -g --all
```

Until then, the GitHub source is still `mohamedelghazali/TSAR`; use the existing slug as a temporary source.

The flags mean:
- `-g` / `--global`: install in the user's global skill locations rather than the current project.
- `--all`: install all valid skills found in this repository to all agents detected by the CLI, without interactive selection.

AIGENT-SEC publishes six Agent Skills-compatible packages:
- `aigent-sec`: primary governance skill and navigation entry point.
- `crypto-inventory`: cryptographic bill-of-materials workflow.
- `secret-scanner`: hardcoded-secret detection workflow.
- `secure-review`: static application-security review workflow.
- `threat-modeler`: STRIDE threat-model generation workflow.
- `security-audit`: adversarial source-first auditing, with complete upstream companion references and validators.

A skill is discoverable only when its `SKILL.md` contains valid YAML frontmatter with both `name` and `description`. The name must match the skill directory.

## List available skills before installation

```bash
npx skills add mohamedelghazali/AIGENT-SEC --list
```

## Verify global installation

```bash
npx skills ls -g
```

## Check for updates and update global skills

```bash
npx skills check
npx skills update -g
```

## What global installation provides

The AIGENT-SEC skills become available to compatible agents in other projects under the global scope. Agents generally decide when to load a skill using its name and description and their own discovery behavior.

## Important: global does not mean forced on every turn

Installing a skill globally does not modify every agent's system prompt, train the model, or guarantee that AIGENT-SEC is consulted for every unrelated task. The installed skill is a reusable local copy; updates are explicit unless the platform documents otherwise.

For stronger standing behavior, configure each agent's supported global instruction mechanism with [`AGENT_BOOTSTRAP.md`](../AGENT_BOOTSTRAP.md). The filename and global configuration location differ by agent and operating system; follow current provider documentation. Do not assume one global instruction file controls every agent, and do not overwrite existing user instructions without permission.

## Current-session-only adoption

A chat-only agent can apply governance only for the current conversation and only to the content it can actually retrieve. See [Universal Agent Onboarding](universal-agent-onboarding.md) for the copy-ready prompt and source-verification requirements.

## Enforcement

The skills provide instruction-level guidance. For deterministic checks, also use AIGENT-SEC's scanners, hooks, policy artifacts, CI workflows, tests, and human security review as appropriate. See [Agent Compatibility Matrix](agent-compatibility-matrix.md), [Agent Integration](agent-integration.md), and [Release Qualification](release-qualification.md).
