---
name: maintenance
description: "Quarterly maintenance pass on a project, covering dependencies, security, build/runtime, CI/CD, performance, code maintainability, docs, backups. Produces a dated prioritized report, then proposes fixes one by one. Use when the user wants to run a periodic maintenance pass on a project, or says \"run maintenance\", \"maintenance pass\", \"project maintenance\", \"quarterly checks\", \"/maintenance\", \"lance la maintenance\", \"passe de maintenance\", \"checks trimestriels\". Accepts a targeted zone, for example \"maintenance security\", \"maintenance deps\", etc."
---

Goal: review a project in depth (about every 3 months), produce a **dated prioritized report**,
then **propose fixes one by one** with validation. Audit first (read-only), action afterwards with
consent. **No silent fix, never `git push`.**

## 0. Scope of the run

- `maintenance` with no zone → **full pass**: the 8 zones below.
- `maintenance <zone>` → **a single zone**.
- For security, performance or maintainability alone, outside a maintenance pass, the
  `security-audit`, `performance-audit` and `maintainability-audit` skills can also be invoked
  directly.

Zones, audit file type (`audit-deliverables` §1) and register category (§3):

| Zone | Audit type | Register category | Delegated to |
|---|---|---|---|
| `deps` | `deps` | dependencies | this skill |
| `security` | `security` | security | `security-audit` |
| `build` | `build` | runtime | this skill |
| `ci` | `ci` | CI/CD | this skill |
| `perf` | `performance` | performance | `performance-audit` |
| `docs` | `docs` | documentation | this skill |
| `backups` | `backups` | backups | this skill |
| `maint` | `maintainability` | maintainability, tests | `maintainability-audit` |

## 1. Preamble (always)

1. **Context**: if a `HANDOVER.md` exists at the project root, read it to understand the state of
   the project.
2. **Deliverables**: load the **`audit-deliverables`** skill (`<docs>` root, paths, frontmatter,
   severity scale, register). Root `docs/` by default.
3. **Stack detection**: read the manifests present (`package.json`, `Cargo.toml`,
   `pyproject.toml`/`requirements.txt`, `go.mod`, `Gemfile`, `composer.json`, `Dockerfile`, etc.)
   to pick the tools for each zone. Generic fallback if the stack is unknown.
4. **Comparison with the previous run**: read the last summary `<docs>/maintenance/<date>.md` and,
   per zone, the last audit of the type (`audit-deliverables` §2) for the **deltas** (new vulns,
   dependency drift, performance regressions). The **carried-over debt** = the rows still open in
   `<docs>/debt/register.md`; without a register, the findings left untreated in the previous
   report.
5. **Critical paths**: take them from the takeover summary or the roadmap if there is one,
   otherwise ask the user (features whose failure costs the most, with their entry points and
   modules). With no answer, say so in the brief of the `auditor` agents (§2) and in the summary.
6. **Best effort depending on access**: if a tool, a CLI or a system is not accessible,
   **degrade** and **note it explicitly** (`tools_run` / `not_run` of each audit, "to check
   manually" otherwise). Never pass an estimate off as a check.
7. **Dedicated branch**: before any commit (report or fix), create or switch to a maintenance
   branch, e.g. `chore/maintenance-<YYYY-MM-DD>`. Never a maintenance commit on the default
   branch. The collection (read-only) can happen before branching. The user merges and pushes.

## 2. Collection phase (read-only)

**Proposed split, with consent**: announce one **`auditor`** agent per chosen zone, launched
together in the same message, each returning the audit file of its zone; wait for the go-ahead.
Without consent, run the zones in sequence in the session, with the same method. During this
phase: **change nothing**.

Brief for each `auditor` agent, complete (it does not see the conversation):
- the skill to apply: `security-audit`, `performance-audit` or `maintainability-audit` for the
  delegated zones, otherwise `maintenance` and the zone (`deps`, `build`, `ci`, `docs`,
  `backups`);
- the project path, the scope (all or a module) and the `<docs>` root;
- the trigger `maintenance <YYYY-MM-DD>` and the path of the summary
  `<docs>/maintenance/<YYYY-MM-DD>.md`;
- the detected stack;
- the critical paths and their file paths (§1.5), or "critical paths unknown: leave Exposure empty
  except for hotspots, no Critical on that criterion alone";
- the hotspots from the last `maintainability` audit if it exists.

The live part (browser, dev-server) stays in the main session (§3).

### Zone 1: dependencies (`deps`)
- List outdated, deprecated, unmaintained (`npm outdated`, `cargo outdated`,
  `pip list --outdated`, etc., plus archived repos and old last releases).
- **Tiered upgrade policy** (supply-chain risk on releases that are too fresh):
  - **Security patches** → apply quickly, **after checking the advisory** (maintainer legitimacy,
    patch diff).
  - **Minor versions** → propose **only if the version has matured** (14 to 30 days since
    release; check the date on the registry when feasible). Otherwise "to review on the next run".
  - **Major versions** → **manual flag** + review of the changelog and breaking changes, never
    automatic.
  - **Security fix only available in a minor or a major**: security takes precedence over the
    maturation delay, not over the review. A minor is proposed right away, after checking the
    advisory and reading the changelog. A major is not upgraded unasked: propose it as a priority
    fix (changelog, breaking changes, tests), and if it is too heavy for this pass, propose a
    mitigation (override or resolution of the transitive dependency, disabling the vulnerable
    feature) and keep the register row open at its security severity.

### Zone 2: security (`security`)
Delegate to **`security-audit`**. In short: real scanners preferred (native audit + osv-scanner;
gitleaks, trufflehog as a fallback; semgrep if present), install offered if missing, heuristic
fallback otherwise. It also covers secrets exposed by the CI (shared with the `ci` zone below).

### Zone 3: build and runtime (`build`)
- Cross-check runtime versions and base images with **endoflife.date**: prioritize EOL and near
  EOL.
- Recommend an **LTS or maintained** version (not necessarily the very latest), consistent with the
  tiered policy.
- Check **pinning**: `.nvmrc` / `.tool-versions` / `rust-toolchain` / Docker image digest.

### Zone 4: CI/CD (`ci`)
- Detect the provider from its files: GitHub Actions (`.github/workflows/`), GitLab CI
  (`.gitlab-ci.yml`), Bitbucket Pipelines (`bitbucket-pipelines.yml`), Jenkins (`Jenkinsfile`),
  Azure DevOps (`azure-pipelines.yml`), other.
- **Hygiene** (static reading of the files, always possible, whatever the provider):
  - pinning: actions to a SHA (GitHub, against supply-chain attacks like tj-actions), Docker
    images to a digest or an exact version, Jenkins plugins, remote templates and `include` to a
    fixed ref;
  - least privilege: `permissions:` (GitHub), job token scope (GitLab `CI_JOB_TOKEN`, Azure
    `persistCredentials`), variables limited to deployment environments;
  - outdated actions, images, agents or runners.
- **Shared with the `security` zone**: whatever exposes a secret (secret in clear in a pipeline
  file or in the logs, external code run with the secrets, injection of untrusted expressions) is
  covered by `security-audit`, not here. This zone covers permissions and hygiene.
- **State** (if a CLI is accessible): latest runs through `gh run list` / `glab ci list`, red or
  green, flakiness. **No access** to the CI → static hygiene only, mentioned in the report.

### Zone 5: performance (`perf`)
Delegate to **`performance-audit`**: static analysis (heavy dependencies, bundle, build config,
anti-patterns, back end) and, for a web app, a performance trace in the main session (§3).

### Zone 6: docs (`docs`)
- **Targeted staleness**: docs untouched since significant code changes (git log), broken internal
  links, CHANGELOG gaps against commits and tags, ADRs/DECISIONS missing recent decisions,
  outdated README/install steps.
- Target the docs present: `CLAUDE.md`, `README`, architecture docs, ADRs/`DECISIONS.md`,
  `CHANGELOG`. Propose **targeted updates**, not a rewrite.

### Zone 7: backups (`backups`)
- Find the **presence** of a mechanism (cron, scripts, cloud config, DB dumps, snapshots).
- Check **freshness** against the **documented frequency** (often in the README, an ADR or a
  `.md`); flag if the last backup is late.
- **No access to the backup system** → do not make things up: tell the user **what to check and
  where**.
- No mechanism detected → note the absence and suggest one.

### Zone 8: code maintainability (`maint`)
Delegate to **`maintainability-audit`**: hotspots (churn × complexity), complexity, duplication,
dead code, cycles between modules, coverage if a report exists, declared debt. The trend from one
quarter to the next tells whether the debt is going up or down. Heavy refactors become workstreams
in `<docs>/debt/roadmap.md` (proposed if it exists), not one-by-one fixes.

## 3. Collection follow-ups (main session)

Before writing, gather the "To do in the main session" sections of all returns and ask the user
**at once**:
- proposed tool installs (outside the audited project), then run only the zones concerned again;
- running the tests with coverage, a production build for measurements;
- **live parts**, if the app starts: performance trace of the key pages (`performance-audit` §2)
  through `dev-server`. Results go in the `## Live` section of the `performance` audit;
- critical paths still unknown, other questions.

Confirmed paths: before writing, raise to Critical the candidates that the `maintainability` audit
listed ("critical paths to confirm") and that touch a confirmed path. With no answer, they stay
High and the summary says so.

What is declined or impossible stays "not run" in the audit and in the summary.

## 4. Summary: audits, register, dated report

Per `audit-deliverables`:

1. **One audit file per zone**: `<docs>/audits/<type>/<type>-<YYYY-MM-DD>.md`, type from the table
   in §0, with `trigger: maintenance <date>`. The returns of the `auditor` agents are written as
   is, except for the reclassifications of §3.
2. **Register** `<docs>/debt/register.md`: create it on the first pass if it does not exist; add
   the new Medium and higher findings, add the source to rows already open, propose closing the
   rows whose finding has disappeared.
3. **Summary** `<docs>/maintenance/<YYYY-MM-DD>.md` (`-<zone>` suffix for a `maintenance <zone>`
   run), without copying the findings. For a targeted run, `zones:` lists only the zone handled,
   and "By zone" says the others were not run; `scope:` stays the code scope (all or a module).

Write the summary in the language the user works in; the template below shows the structure.

```markdown
---
type: maintenance
date: <YYYY-MM-DD>
scope: all
zones: [deps, security, build, ci, perf, docs, backups, maint]
audits:
  - <docs>/audits/deps/deps-<YYYY-MM-DD>.md
  - …
register: <docs>/debt/register.md
---
# Maintenance report: <project>, <YYYY-MM-DD>

## Summary
- Detected stack: …
- Critical paths: … (or "unknown")
- Checks actually run and degraded checks: …
- Deltas since the previous run (<date>): new vulns, drifted dependencies, performance regressions…
- Register: <n> open rows (<n> new), <n> closed since the previous pass

## To handle in this pass
The findings kept for §5, in order, with their `TD-xx` and the link to the audit.

## By zone
One line per zone: verdict, link to the audit (or "not run" for a targeted run).
```

**Commit audits, register and summary together** on the maintenance branch:
`docs(maintenance): report <date>`.

## 5. Proposed fixes (one by one, in the main session)

Go through the findings in the order **critical security and EOL → quick wins (high impact, low
effort) → the rest**. Exception: heavy refactors from the `maint` zone are not proposed here; they
go into the roadmap (see `maintainability-audit` §11). For each one:
1. Present the finding, the proposed fix and the risk.
2. Wait for the user's validation (apply / skip / postpone).
3. If applied: make the change, check (build, tests), then **one commit per fix, or per validated
   batch of the same type** (several fixes from the same zone approved at once). Conventional type
   and scope by zone (`chore(deps): bump minor`, `docs: refresh README`,
   `ci: pin actions to SHA`…); a single commit never mixes two zones. The register update goes in
   the same commit: `TD-xx` row closed (date and commit); a roadmap workstream whose rows are all
   closed moves to "done". A skipped or postponed fix leaves its row open: it is the carried-over
   debt of the next pass.
4. **Never run `git push`**: the user pushes.

## 6. Resuming across sessions

A full run can span several sessions. **Keep a running checkpoint in `HANDOVER.md`** (with
`dev-workflow:handover` if the `dev-workflow` plugin is installed; otherwise skip): zones done and
remaining, collection follow-ups pending, findings waiting for a decision. A new session picks up
exactly where the previous one stopped.
