# TSAR Release Qualification

This document separates the historical v1.1.1 release qualification from verification of the current `main` snapshot. A successful repository CI run is not evidence of a published release or a live cloud deployment.

## Historical v1.1.1 Release

- Repository: `mohamedelghazali/TSAR`
- Version: `1.1.1`
- Tag: `v1.1.1`
- Qualified commit: `61dce3e6d46dd25dfc0ad05617329d7ba89d43a5`
- Qualified tree: `a4ba503222ceed395bdb81f48b43ebb313bbeffd`
- Snapshot reviewed: 2026-10-31
- GitHub Release: [TSAR v1.1.1 — Stable Release](https://github.com/mohamedelghazali/TSAR/releases/tag/v1.1.1)
- Published at: 2026-10-31 21:22:51 UTC

The v1.1.1 qualification below applies only to that historical source snapshot. It must not be interpreted as qualification of later commits now present on `main`.

### Historical evidence

- The inventory recorded 171 active rule files across 37 rule domains, with all manifest references resolving at that snapshot.
- The inventory recorded 15 agent-specific prompts plus the universal prompt.
- The complete release gate passed on the qualified commit; its log reported 186 pytest tests passed.
- The historical main ruleset and release status were recorded at that time.
- The GitHub Release had no separately attached binary assets; GitHub provided source archives.

The historical inventory and CI evidence are retained as release records, not asserted as a fresh inventory of the current tree.

## v1.2.0 — Stable Release, 2026-11-18

- Branch: `main`
- Commit: `fb666df0cb4609624a287ccd59006b50051c6b55`
- Commit subject: `chore(web): align Next.js 16 and React 19 dependencies (#92)`
- Version files are aligned at `1.2.0` (`VERSION`, `manifest.yaml`, CLI, LSP, and web package metadata). Status: v1.2.0 — Stable Release, 2026-11-18 (published stable baseline; 8/8 gate checks, 326 tests passed).

### Current CI evidence

The post-merge workflows for the current main commit completed successfully:

- The current commit's release-gates workflow completed successfully: [run 42410222144](https://github.com/mohamedelghazali/TSAR/actions/runs/42410222144).
- The full verification job reported **326 pytest tests passed** and `ALL CHECKS PASSED`.
- The post-merge check-run set contains **8/8 successful checks**.
- Terraform static validation, infrastructure validation, Kubernetes schema validation, TSAR validation, self-test, Claude Code Windows Hook Compatibility, and orchestrator checks completed successfully.

This is evidence of repository-level validation for this commit. It is not evidence of a live AWS deployment or an independently audited production environment.

### Current GitHub governance

The active ruleset `TSAR-Main-Protection` targets `refs/heads/main` and currently enforces:

- Pull requests for changes to main.
- Review-thread resolution.
- No branch deletion.
- No non-fast-forward updates.
- Required linear history.
- Zero required approving reviews.

The ruleset contains a `required_status_checks` rule with strict policy enabled, but its `required_status_checks` list is **empty**. Consequently, no individual CI check is actually required for merging yet. A repository administrator must populate that list with the exact observed check names: `Full verification (OPA, LSP, Terraform, pytest)`, `TSAR Self-Test`, `Claude Code Windows Hook Compatibility`, `Infrastructure Validation`, `TSAR Validate Rules`, and `TSAR Orchestrator`. The Terraform and Kubernetes child jobs are currently aggregated by the `Infrastructure Validation` job.

A second qualified maintainer's approval is recommended when one is available. No approval requirement is represented as active today.
## TSAR v1.2.0 — Stable Release (tag `v1.2.0`, 2026-11-18)

Version `1.2.0` is published as `TSAR v1.2.0 — Stable Release` (tag `v1.2.0`, 2026-11-18). Version metadata is aligned across `VERSION`, `manifest.yaml`, the CLI package, the LSP package, and the web package.

Repository CI passes on the qualified snapshot (8/8 checks; 326 tests). The 1.2.0 wheel and sdist distributions are built, verified, and attached to the published GitHub Release with GitHub SLSA build provenance. Qualification for the TSAR core release is GitHub-only: repository CI, package/build verification, workflow validation, provenance configuration, and release metadata. No external AWS account setup, AWS provisioning, or live AWS test was required for publishing the TSAR core release.

The AWS WORM service remains a separately scoped deployment candidate. Its code, Terraform, static checks, isolated tests, and GitHub workflow configuration may be reviewed in GitHub, but without a live AWS deployment it must not be described as operational or production-verified. This exclusion does not affect the published TSAR core `v1.2.0` release.

## AWS WORM Service — Implementation vs. Operation

PR #67 added the AWS Lambda anchor service, Terraform infrastructure, KMS Ed25519 signing, S3 Object Lock COMPLIANCE retention, DynamoDB sequencing/idempotency, trust export tooling, and isolated behavioral/contract tests.

The following boundaries are explicit:

- The service code and infrastructure definitions are present in the repository.
- CI validates code and infrastructure statically and runs isolated tests.
- No AWS resources have been provisioned by the GitHub workflow. The workflow is now merged and can deploy only through an explicit manual dispatch using GitHub OIDC; it must complete a live apply and smoke test before operational status can be claimed.
- No live AWS integration test has been completed.
- No AWS credentials, production secrets, or deployed endpoints are included in the repository evidence.
- S3 and DynamoDB do not share a transaction; a retained orphan S3 object can remain if the DynamoDB transaction fails.

Therefore, the AWS WORM service is an implemented deployment candidate, **not an operational or production-verified service**. Operational qualification requires a successful GitHub Actions OIDC deployment and live verification of authenticated append, KMS Ed25519 receipt signature, durable latest-anchor read, idempotent retry, S3 Object Lock controls, and publication of the public KMS trust artifact for TSAR clients.

## Staging Scope

A separate Staging environment is **not a required project milestone** for TSAR. The core rules, CLI, OPA/LSP integrations, and GitHub workflows are validated through local tests and CI. If the AWS WORM service is later deployed, it can be validated in an isolated AWS account or explicitly bounded test deployment; this does not create a requirement for a permanent, general-purpose Staging environment.

## Qualification Decision

| Scope | Decision |
|---|---|
| Historical v1.1.1 release | Qualified only for its recorded tag and commit |
| Current main repository CI | Pass on `fb666df0cb4609624a287ccd59006b50051c6b55` (8/8; 326 tests) |
| TSAR v1.2.0 — Stable Release | Published as tag `v1.2.0` (2026-11-18); GitHub-only qualification path passed 
| AWS WORM operational behavior | Out of scope for core release; not verified and not operational |
| Separate Staging environment | Not required |

Do not move or retarget the historical `v1.1.1` tag. The 1.2.0 candidate requires successful CI and the acceptance evidence above. Do not publish a tag or release until those conditions are met.

This qualification does not certify absence of vulnerabilities, guaranteed agent prompt compliance, regulatory compliance, or live cloud deployment behavior.
