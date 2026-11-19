---
name: security-audit
description: "Security posture audit of a whole project: dependency vulnerabilities, secrets, configuration, SAST, and abuse controls promised by living specs. Prefers real scanners (osv-scanner, gitleaks, semgrep, native audit) and offers to install them when missing. Use when the user wants a security audit of the whole project, or says \"security audit\", \"vulnerability scan\", \"scan for secrets\", \"audit de sécurité\", \"scan de vulnérabilités\". Different from the built-in /security-review, which audits the current diff. Reused by the maintenance (security zone) and legacy-takeover skills."
---

Goal: audit the **overall security posture** of a project. For the current diff, use the built-in
`/security-review`. Usable on its own, or called by `maintenance` (`security` zone) or
`legacy-takeover`. Audit first, read-only; fixes afterwards, with consent. **Never run
`git push`.**

## Method: real tools first

Prefer **reference scanners**; fall back on heuristics only as a last resort, and **state what
actually ran and what was estimated** (`tools_run` / `not_run` in the frontmatter, Source column of
each finding, per `audit-deliverables` §2).

For each category: check the tool is present (`command -v <tool>`); if it is missing, **offer to
install it** outside the audited project (`brew`, `pipx`, binary, one-off `npx --yes`), never as a
project dependency; if the user declines or the install fails, heuristic fallback and an explicit
note.

**Called through the `auditor` agent**: it can neither install nor ask. Direct heuristic fallback,
tool listed in `not_run`, and the install proposed under "To do in the main session" (same
principle as `maintainability-audit` §0.4). The session runs the unit again once the tool is
installed.

### 1. Dependency vulnerabilities
- Native audit for the stack: `npm audit` / `pnpm audit`, `cargo audit`, `pip-audit`,
  `bundle audit`, `govulncheck`…
- **osv-scanner** (multi-ecosystem) on top: `osv-scanner --recursive .`.
- Cross-check with the **tiered policy** of the `maintenance` skill (`deps` zone): a security patch
  is checked (legitimate advisory, clean diff) before it is applied, because even a recent release
  can be a supply-chain vector.

### 2. Secrets
Absolute rule: **no secret value is ever displayed**, in full or in part. A secret is reported by
its file, its line and its type.

- **gitleaks** first, on the working tree (uncommitted files included), redacted output:
  `gitleaks dir . --redact --no-banner` (gitleaks 8.19 and later; before that:
  `gitleaks detect --no-git --source . --redact`).
- **Git history** only if the user asks for it (slower, surfaces secrets already rotated):
  `gitleaks git . --redact`.
- **trufflehog** only if gitleaks is missing and cannot be installed. Its output contains the value
  in clear: switch it to JSON and strip the value fields before reading anything,
  `trufflehog filesystem . --no-verification --json | jq -c 'del(.Raw, .RawV2, .Redacted)'`.
  `--no-verification` avoids sending the secret to the provider to test it.
- **Fallback** (no scanner): `grep` for common patterns (AWS keys, `-----BEGIN`, `api_key`,
  `password=`, `ghp_` tokens, `xox`) keeping only the path and line
  (`grep -rnE '<pattern>' . | cut -d: -f1,2`), never the matched text.
- Any secret found: **Critical**, recommend **immediate rotation** (removing it from the file is
  not enough: it stays in the history and may already have leaked).

### 3. SAST (if available)
- **semgrep** with rulesets suited to the stack (`semgrep scan --config auto` or targeted
  rulesets). Otherwise, a targeted heuristic review: injections, deserialization, access control,
  hard-coded secrets, weak crypto.

### 4. Configuration and supply chain
- Lockfile integrity, dependency confusion (internal and public packages with the same name),
  exposed surfaces (ports, debug endpoints), security headers and CORS for a web app, sensitive
  files committed (`.env`, keys).
- **CI, shared with the `ci` zone of `maintenance`**: this audit covers what exposes a secret or
  gives untrusted code access to secrets (secret in clear in a pipeline file, secret printed in the
  logs, `pull_request_target` or equivalent running the code of an external contribution with the
  secrets, injection of untrusted expressions into a script). The `ci` zone covers hygiene:
  `permissions:` and token scope, pinning of actions and images, outdated versions. When invoked
  alone, without a `ci` zone in the same pass, this audit also reports overly broad permissions;
  the register deduplicates (same finding, same place).

### 5. Abuse controls promised by the specs (if `docs/specs/features/` exists)
These specs follow the living specs format of the `living-specs` plugin. If that plugin is
installed, its `living-specs:functional-spec` skill defines the format (abuse grid in its
`abuse.md`); otherwise read the feature sheets as they are.

- Read the "Abuse and limits" section of each feature sheet. For each **controlled** abuse, look
  in the code for the control of its `BR-xx`: scope check, cap, rate limit, neutralization on
  export.
- Finding when the control is missing, or present only on the client (a disabled button, form
  validation with no server equivalent). Location: the sheet and the `BR-xx` on one side, the
  endpoint or module on the other. Source: `heuristic review (spec)`.
- An **accepted** abuse is not a finding. A sheet without an "Abuse and limits" section is
  reported once, as Low, pointing to `living-specs:functional-spec` if the plugin is installed.
- Severity guide: missing scope check on personal data or an export → High (Critical if the
  endpoint is exposed outside the internal network); missing cap or rate limit → Medium.

## Severity

Shared scale from `audit-deliverables` §2. Guide: committed secret, exploitable vulnerability on an
exposed surface → Critical; known vulnerability with no obvious exploitation, SAST finding
confirmed on reachable code → High; weak configuration, vulnerable dependency that is not reachable
→ Medium; hardening → Low.

## Output

Deliverables per the **`audit-deliverables`** skill (path, frontmatter, common columns, debt
register), type `security`. Write the report in the language the user works in. For each finding:
severity, effort, risk, location, actionable recommendation. In a standalone audit, the Exposure
column stays empty unless the user gave critical paths (`audit-deliverables` §2).

- **Called by `maintenance` or `legacy-takeover`**: return the collection (read-only), no fixes
  here: the orchestrator writes the file and proposes the fixes.
- **Invoked alone** (`audit-deliverables` §6):
  1. Branch `chore/security-audit-<YYYY-MM-DD>` at the latest before the first commit (or the
     non-default branch already in use).
  2. Write `<docs>/audits/security/security-<YYYY-MM-DD>.md`, update the register if it exists,
     commit the report alone: `docs(audit): security <date>`.
  3. Propose the fixes **one by one**, secrets and Critical first, with validation; one commit per
     fix or per validated batch of the same type, recorded under "Applied fixes", `TD-xx` row
     closed.
  4. **Never run `git push`.**
