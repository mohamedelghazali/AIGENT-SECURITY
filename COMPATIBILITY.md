# AIGENT-SEC Agent Compatibility

AIGENT-SEC supports multiple integration paths. They are related but not interchangeable.

## 1. Agent Skills CLI

The Vercel Skills CLI supports repository sources, global scope, and installation to all detected compatible agents.

After the GitHub repository slug has been renamed to `AIGENT-SEC`, use:

```bash
npx skills add mohamedelghazali/AIGENT-SECURITY -g --all
```

Until the slug migration is completed, the existing GitHub source remains `mohamedelghazali/AIGENT-SECURITYURITY`; use that slug for installation in the interim.

- `-g` / `--global` requests user-level installation.
- `--all` installs all valid skills to all agents detected by the CLI without interactive selection.
- The CLI may report agents that do not support the requested installation scope.
- Consult the current [Vercel Skills CLI command documentation](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## 2. Agent instruction integrations

The [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md) documents the provider/product-specific instruction files and their supported project or system-instruction paths.

These integrations require the configuration mechanism offered by each product. They are not automatically installed by the Skills CLI and are not privileged provider-level security controls.

## 3. Chat-only models

A model that can only receive a URL and return text, with no repository browsing, shell, filesystem, connector, or persistent-instruction access, cannot install AIGENT-SEC or change its future sessions. It can apply only the content actually retrieved for the current conversation.

## 4. Persistence and enforcement

- Global skills can be reused across projects by compatible agents within the installing user account.
- Skill activation is controlled by each agent; global installation does not guarantee loading on every turn.
- Global bootstrap instructions must be configured separately through each agent's supported mechanism.
- Scanners, hooks, policy enforcement, CI checks, and human review provide stronger assurance than prompts alone.
- The Cloudflare-derived `security-audit` skill is packaged with all companion references and validators so that it remains usable when installed as an individual skill.

## 5. Legacy compatibility

Existing CLI commands, Python module names, package distribution identifiers, manifest schema namespace, and several internal tool paths retain historical `tsar` identifiers for compatibility. These identifiers are not the public product identity. Removing them requires a separately verified migration and must not silently break existing workflows.
