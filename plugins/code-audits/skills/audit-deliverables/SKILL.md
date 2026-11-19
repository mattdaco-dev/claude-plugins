---
name: audit-deliverables
description: "Shared convention for audit deliverables: where an audit report goes (<docs>/audits/<type>/, docs/ by default), its traceability frontmatter, the severity scale and the common finding columns, the living tech debt register (<docs>/debt/register.md) and the roadmap, the maintenance and takeover summaries. Load it from security-audit, performance-audit, maintainability-audit, gdpr-audit, seo-audit, maintenance, legacy-takeover and the auditor agent before writing or returning a report, or reading a previous one. Use when the user asks where audit reports go, or says \"audit deliverables\", \"debt register\", \"tech debt register\", \"where are the audit reports\", \"livrables d'audit\", \"registre de dette\"."
---

Goal: a finding can be found again and tracked, whichever skill produced it. An audit is the same
object whether it runs on its own, from `maintenance` or from `legacy-takeover`; the debt is a
living state that all of them keep up to date.

Write the reports in the language the user works in. File names, folder names, frontmatter keys,
IDs, severity labels and section anchors stay as defined here.

## 1. Tree

Root `<docs>`: the project's `docs/` by default. If the user does not want anything written in the
repo, use the path they give, and nothing is committed. In every template and frontmatter, replace
`<docs>` with the real root (`docs/` most of the time).

```
<docs>/
├── audits/<type>/<type>-<YYYY-MM-DD>[-<scope>].md   one file per audit, never edited afterwards
├── debt/
│   ├── register.md            living state: TD-xx rows
│   └── roadmap.md             living state: WS-xx workstreams, chosen order
├── maintenance/<YYYY-MM-DD>[-<zone>].md   summary of a maintenance pass
└── takeover/<YYYY-MM-DD>-quick.md    legacy-takeover quick mode
    takeover/<YYYY-MM-DD>.md          summary of a full takeover
```

- **Types**: `security`, `performance`, `maintainability`, `gdpr`, `seo`, and the `maintenance`
  zones that have no dedicated skill: `deps`, `build`, `ci`, `docs`, `backups`.
- **Scope**: add a suffix only when the audit does not cover the whole project
  (`security-2026-10-12-billing.md`). Same type, same day, same scope: suffix `-2`.
- **One audit = one file**: domains (GDPR D1…) run in parallel are sections of the same file, and
  so is the live part.
- **Snapshots and state**: a file in `audits/`, `maintenance/` or `takeover/` records what was seen
  that day and is never changed again, with two exceptions: the "Applied fixes" section of an
  audit, and the "Next steps" section of a takeover summary (quick or full), where
  `legacy-takeover` records the next steps that were done, skipped or postponed. `debt/` gets
  updated.

## 2. Audit file

Mandatory frontmatter:

```yaml
---
type: security
date: 2026-10-12
scope: all                            # or the module / directory
trigger: standalone                   # or "maintenance 2026-10-12", "legacy-takeover 2026-10-12"
summary: <docs>/maintenance/2026-10-12.md   # absent when standalone
previous: <docs>/audits/security/security-2026-07-10.md   # absent if there is none
tools_run: [osv-scanner 1.9.2, gitleaks 8.21.0]
not_run: [semgrep (missing, heuristic fallback)]
---
```

`tools_run` and `not_run` state what actually ran and what was estimated: every audit skill fills
them in, and never passes an estimate off as a measurement.

Body: the audit skill's template (title, summary, detail by zone or domain, specific sections such
as "outside the code" for GDPR), with a findings table that **always** starts with these columns,
in this order:

| # | Severity | Effort | Risk | Exposure | Source | Finding | Where | Recommendation |
|---|---|---|---|---|---|---|---|---|

- Severity: from the scale below. Effort: S / M / L. Risk: of regression, low / medium / high.
  Source: `tool` or `reading`. Where: `path:line`.
- Exposure: hotspot, critical path, stable code, or empty if unknown. In a standalone audit,
  critical paths are usually not known: the column stays empty, unless the user gave them or the
  audit computes hotspots itself (`maintainability`). Say so in one line in the report summary.
- Type-specific columns come **after** these (GDPR article, SEO impact, Domain, Zone).
- A `## Live` section if a live part ran (performance trace, Lighthouse, cookies).
- A `## Applied fixes` section, only if the audit is standalone and proposes fixes: one line per
  fix (finding `#`, commit, `TD-xx` closed).

### Severity scale (shared by every audit)

| Severity | Meaning |
|---|---|
| Critical | exploitable or already causing harm, to handle before anything else (committed secret, exploitable vulnerability on an exposed surface, exposed EOL runtime, clear breach of the law, key page that cannot be indexed) |
| High | real short-term risk, to handle in the current pass |
| Medium | debt that already costs something, to plan; goes into the register |
| Low | improvement or comfort, stays in the audit |

The four labels are written exactly like this (`Medium`, never `Med`). Each audit skill can give
examples specific to its domain without changing the scale.

**Comparison with the previous audit**: the most recent file in `<docs>/audits/<type>/`; otherwise
the older path `<docs>/<type>/<date>.md` (or `<docs>/maintenance/<date>.md` for a zone);
otherwise none.

## 3. Debt register

`<docs>/debt/register.md`. Created by `legacy-takeover` (full mode), or by `maintenance` on its
first pass. A standalone audit updates it if it exists, without creating it.

| ID | Status | Category | Finding | Where | Severity | Exposure | Effort | Source | Opened | Closed |
|---|---|---|---|---|---|---|---|---|---|---|
| TD-07 | open | security | … | `path` | High | critical path | M | [security-2026-10-12 #3](../audits/security/security-2026-10-12.md) | 2026-10-12 | |

- **ID** increasing, never reused. **Status**: `open`, `resolved` (Closed = date and commit),
  `dropped` (Closed = date and reason in one line).
- **Adding**: each Medium or higher finding of a new audit, unless it matches an open row (same
  finding, same place): then add the source to that row. Two distinct findings on the same file
  make two rows. Low findings stay in the audit.
- **Closing**: an applied fix closes its row. If the finding of an open row no longer appears in a
  new audit of the same type and scope: propose closing it, do not do it alone.
- **Categories**: security, maintainability, tests, dependencies, runtime, CI/CD, backups,
  performance, GDPR, SEO, documentation. Mapping from the audit type:

  | Audit type | Category |
  |---|---|
  | `security` | security |
  | `performance` | performance |
  | `maintainability` | maintainability; tests for coverage and test findings (§6 of `maintainability-audit`) |
  | `gdpr` | GDPR |
  | `seo` | SEO |
  | `deps` | dependencies |
  | `build` | runtime |
  | `ci` | CI/CD |
  | `docs` | documentation |
  | `backups` | backups |

- The **carried-over debt** of a pass = the rows still open.

## 4. Roadmap

`<docs>/debt/roadmap.md`. Created by `legacy-takeover` (full mode), or by `maintenance` on request.
Workstreams `WS-xx` grouped in phases (stabilize, set up the safety net, refactor, modernize). Each
workstream: goal, `TD-xx` handled, prerequisites, effort, risk, done criterion, **status** (to do,
in progress, done). A dated "Chosen order" section, once the user has decided. A workstream moves
to "done" when all its `TD-xx` are closed.

## 5. Summaries (maintenance, takeover)

Frontmatter:

```yaml
---
type: maintenance              # or takeover-quick, takeover
date: 2026-10-12
scope: all                     # or the module / directory
zones: [deps, security, build, ci, perf, docs, backups, maint]   # maintenance only: zones covered
audits:                        # the audit files produced by this pass
  - <docs>/audits/security/security-2026-10-12.md
  - <docs>/audits/deps/deps-2026-10-12.md
register: <docs>/debt/register.md
---
```

Body: the orchestrator's template. Findings are not copied into it: it points to the audits and to
the register (open rows, closed rows, new rows since the previous pass).

## 6. Who writes what

- **`auditor` agent**: returns the complete audit file (frontmatter included) as text, without
  writing it. The session writes it as is.
- **Multiple returns**: when one audit is split (one `auditor` agent per domain or zone), the
  session merges the returns into a single file: frontmatters merged (`tools_run` and `not_run` as
  a union), findings renumbered in a single series.
- **Standalone audit**: writes its audit file, updates the register if it exists, then the
  "Applied fixes" section as fixes go in.
- **Orchestrator** (`maintenance`, `legacy-takeover`): writes the audit files returned by the
  `auditor` agents, its summary, the register and the roadmap.
- **Branch**: never work or commit directly on the default branch (`main`/`master`). A standalone
  audit runs on `chore/<type>-audit-<YYYY-MM-DD>` (e.g. `chore/security-audit-2026-10-12`),
  created at the latest before the first commit; if the session is already on a branch other than
  the default one, keep working on it. The collection, read-only, can happen before. Fixes follow
  on the same branch. The orchestrator has its own branch (`chore/maintenance-<date>`, the
  takeover branch).
- **Commits** (Conventional Commits): `docs(audit): <type> <date>` for a standalone audit, report
  only, before any fix; then one commit per fix, or per validated batch of the same type (several
  fixes approved at once by the user, never two types or two zones in one commit). The
  orchestrator commits its audits with its summary (`docs(maintenance): report <date>`,
  `docs(takeover): …`). `<docs>` root outside the repo: nothing is committed. Never run
  `git push`: the user pushes.
