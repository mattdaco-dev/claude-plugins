---
name: legacy-takeover
description: "Takeover of an existing or legacy project, in two modes. Quick: one page to know where to dig (stack and EOL, size, activity, hotspots, red flags, risk map). Full: audits in parallel through the auditor agent, tech debt register and phased roadmap. Each mode then proposes its next steps one by one, without touching the code. Use when the user takes over a codebase, or says \"legacy takeover\", \"take over this project\", \"project assessment\", \"onboarding on this codebase\", \"project overview\", \"overall tech debt\", \"reprise legacy\", \"reprendre un projet\", \"état des lieux du projet\", \"audit de reprise\"."
---

Goal: take charge of a project you did not write, and come out with a **risk map** and a
**roadmap**, not a pile of findings. This skill orchestrates: the expertise lives in the skills it
calls (`maintainability-audit`, `security-audit`, `performance-audit`, `maintenance`,
`gdpr-audit`, `seo-audit`, `c4-architecture`, and, when their plugins are installed,
`living-specs:retro-spec`, `living-specs:ticket-writing` and `dev-workflow:adr`). **Never run
`git push`.**

The takeover is **proactive but does not touch the code**: at the end of each mode, it goes through
its next steps one by one (§1.9, §3), the way `maintenance` goes through its fixes. A step that
changes the code hands over to the skill concerned (`security-audit`, `maintainability-audit`…),
which applies its own procedure; the takeover stops there for that step.

Write the reports in the language the user works in. File names, frontmatter keys, IDs and
severity labels stay as defined in `audit-deliverables`.

## 0. Choosing the mode

- `legacy-takeover quick`: overview, a few minutes to an hour depending on size.
- `legacy-takeover full [scope]`: complete audits, on the whole project or on the given modules.
  It needs the **`auditor`** agent (shipped with this plugin): without it, no full mode; say so and
  stick to the quick mode, or run the audits one by one in the main session if the user prefers.
- `legacy-takeover` alone: quick mode if there is no quick report less than a month old in
  `<docs>/takeover/`, otherwise ask quick or full. The existing quick report is only looked for
  there: a quick report stored elsewhere is reused only if the user gives its path, do not ask for
  it.

The quick mode is the entry point of the full mode: on a large project, it points to the scope
where the full mode is worth it. A full run without a recent quick report starts by making one.

Shared principles:
- **Read-only until the reports.** No build, no tests, no install during collection.
- **Untrusted code**: linters and analysers that load the project's config (`eslint.config.js`,
  `knip.config.ts`, a Vite or Webpack config) execute its code, and so does `dev-server`. Before
  the first such tool on a project the user did not write, say so and offer to work in a
  container or VM; if they decline, keep to the tools that only read files (gitleaks, osv-scanner,
  semgrep, cloc) and record the others as "not run".
- **Honesty**: each finding says whether it comes from a tool that ran, from reading the code, or
  from an estimate. What could not be checked is listed, not guessed.
- **Secrets**: only the location and the type, never the value or the line. Every secret search
  runs with an output that shows no content (§1, point 6).
- **Deliverables** per the **`audit-deliverables`** skill, to load first: audits in
  `<docs>/audits/<type>/`, living state in `<docs>/debt/` (register, roadmap), takeover snapshots
  in `<docs>/takeover/`. The same files are kept by `maintenance`: a takeover that finds an
  existing register or roadmap completes them, it does not recreate them.
- **`<docs>` root**: `docs/` by default. The project may not be yours: if the user does not want
  anything written in the repo, the root is the path they give, nothing is committed, and
  `HANDOVER.md` is ignored through `.git/info/exclude` rather than `.gitignore`. In this "nothing
  in the repo" mode, everything the takeover would write into the project goes under `<docs>`:
  draft context file (§3.1), ADR register (§3.3), tickets (§3.4), and no glossary is created in the
  repo (`c4-architecture` §8).
- **Branch** `chore/takeover-<YYYY-MM-DD>` before the first commit (never commit on the default
  branch). A full run continues on the quick run's branch if it still exists and is not merged,
  otherwise it creates one at its own date. Called skills that have their own branch
  (`living-specs:retro-spec`, `c4-architecture`) stay on the takeover branch.

## 1. Quick mode

No agent and no install: `git`, reading, `grep`, plus network access for endoflife.date, and
`structurizr` if it is already installed (C4 diagram in point 7). A `cloc` already present can
replace the size command; no complexity tool.

1. **Identity**: README, `docs/`, ADRs, manifests. What the app does in three sentences, how
   reliable the docs are (last change vs last commit).
2. **Stack and versions**: languages, frameworks, runtime, base images. Compare with
   endoflife.date (WebFetch, or `curl -s https://endoflife.date/api/<product>.json`): EOL, close
   to EOL (less than 6 months), maintained.
3. **Size and structure**: physical lines per extension (comments and blank lines included),
   tracked text files only:
   `git grep -I -c '' -- . ':!<excl>' | awk '{c=$0; sub(/.*:/,"",c); p=substr($0,1,length($0)-length(c)-1); sub(/.*\//,"",p); e=(p ~ /\./) ? p : "(none)"; sub(/.*\./,"",e); s[e]+=c} END {for (k in s) print s[k], k}' | sort -rn`
   (`<excl>`: generated code, vendored code, lockfiles, fixtures; one exclusion per
   `':!<pattern>'`). The count is taken after the last `:`, which holds with a `:` in a file name.
   Then the main modules or packages and their weight.
4. **Activity**: `git rev-list --count --since=12.months HEAD`, date of the last commit,
   `git shortlog -sn --since=6.months HEAD` (active) against `git shortlog -sn HEAD` (all; `HEAD`
   is required, otherwise `shortlog` reads standard input and returns nothing). A repo without
   history (export, squash) is reported as such.
5. **Hotspots**: churn × size, with the command and thresholds of `maintainability-audit` §1,
   without complexity. Top 10, with tests yes/no.
6. **Red flags** (presence or absence, no fine analysis):
   - probable secrets, **files only**: `git grep -lIE '<patterns>'` (e.g.
     `BEGIN [A-Z ]*PRIVATE KEY|password\s*[=:]|api[_-]?key\s*[=:]|AKIA[0-9A-Z]{16}`), and
     `git ls-files | grep -E '(^|/)\.env($|\.)'` for a versioned `.env`; never open these files;
   - no lockfile, framework or runtime one major version or more behind, or EOL;
   - no tests, or no tests on the hotspots;
   - no CI, or a CI that does not run the tests;
   - declared debt: number of `TODO`/`FIXME` per 1000 lines, compiler workarounds
     (`@ts-ignore`, `@SuppressWarnings`…); a qualitative marker, flagged above 5 per 1000;
   - visible personal data (`User` models, `email`, `iban` fields…): a hint to propose
     `gdpr-audit`.
7. **Risk map**: one table per module (size, churn, tests, red flags, level). **High** level:
   hotspot without tests, or a security red flag, or EOL runtime; **medium**: tested hotspot, or a
   large module without tests; **low**: the rest. Then the 3 to 5 major risks of the project, one
   sentence each.
   **Diagram**: context and containers through `c4-architecture` quick mode (its §8, which also
   sets the risk level of each container, shown by its border). The quick report points to
   `<docs>/architecture/workspace.dsl` and its README (command to regenerate the site), without
   copying the diagram; the local site is only cited as a convenience link.
8. **Where to dig**: the scope or scopes proposed for a full run, and the list of audits that
   follows from it (§2.2).

Output: `<docs>/takeover/<YYYY-MM-DD>-quick.md`, summary frontmatter `type: takeover-quick`
(`audit-deliverables` §5, without `audits:` since the quick mode runs none), **one page**: the
eight points above, tables rather than prose. Commit the quick report, the C4 model and the
glossary if `c4-architecture` created or completed it: `docs(takeover): quick overview <date>`.

### 1.9 Next steps (quick)

Present the numbered list, then go through one step at a time: **do / skip / later**. Keep only
the ones that apply.

1. **Emergencies**, only if the quick mode found a committed secret, an exposed EOL runtime or an
   obvious vulnerability: propose handling them without waiting for the full mode, by handing over
   to `security-audit` (or `maintenance` zone `build` for EOL) limited to these findings. A secret
   gets rotated: removing it from the file is not enough.
2. **Partial context file** (§3.1): stack, structure, commands read, risks from the quick report;
   sections still empty marked "to complete after the full run".
3. **Full run** on the scope named in point 8, with the proposed list of audits: with consent,
   continue with §2 without redoing the quick mode.

Skipped or postponed steps are recorded in the quick report ("Next steps" section), to be proposed
again at the next launch.

## 2. Full mode

Full-run summary: `<docs>/takeover/<YYYY-MM-DD>.md` (frontmatter `type: takeover`, list of the
audits produced). It opens at §2.3 and is completed at §2.9.

The C4 model is completed at §2.8, once the register is in place.

### 2.1 Framing

- A quick report less than a month old is present, otherwise make one first (§1).
- Scope: the whole project, or the modules the user chose from the quick report.

### 2.2 Audits

**Base, always**: `security-audit`, `maintainability-audit`, `performance-audit` (its static part
applies to any project, back end included), and the `deps`, `build`, `ci`, `docs`, `backups` zones
of `maintenance`.

**Depending on the project**, proposed from the quick report:
- web front end: `seo-audit` only if the site is public and meant to be indexed;
- personal data: `gdpr-audit`.

Present the list to the user and wait for validation. It counts as consent to launch the agents.
If §2.3 reveals a need the quick mode had not seen (personal data), reopen the list before
launching.

### 2.3 Light functional view and critical paths

If the `living-specs` plugin is installed: phase 1 of `living-specs:retro-spec` only (mapping,
features and criticality), without writing `docs/specs/` and without creating its dedicated branch
(the "Branch" step of its preamble): stay on `chore/takeover-<date>`. Otherwise, list the features
and their criticality yourself from the routes, screens and modules, and have the user validate
them. Then:
- **Critical path** = a feature rated Critical or High, validated by the user, who can add or
  remove some. This feature criticality is a different scale from the audit severity
  (`audit-deliverables` §2): a Critical feature does not make its findings Critical.
- For each path, record its **file paths**: entry points (routes, controllers, screens) and the
  modules or directories that carry it. Without them, no audit can link a hotspot to a path.
- Write it all in the "Features and critical paths" section of the summary (features,
  criticality, paths kept and their file paths).

### 2.4 Parallel collection

- One **`auditor`** agent per unit, all launched in the same message. Unit = an audit, a
  `maintenance` zone, or a `gdpr-audit` domain (D1…): the agent cannot parallelize by itself.
- Brief for each one:
  - the skill (and the zone or domain), the project path, the scope;
  - the `<docs>` root, so it looks there for the previous audit and puts its output path there;
  - the trigger `legacy-takeover <date>` and the path of the summary;
  - the detected stack and the hotspots from the quick report (table of point 5);
  - "critical paths validated by the user, with their file paths: <list>. Use them for severity
    instead of asking for them."
- Write each return as is at the path it gives (`<docs>/audits/<type>/…`). The units of the same
  audit (GDPR domains) are grouped as sections of a single file.

### 2.5 Collection follow-ups

Before the register, gather the "To do in the main session" sections of all returns and ask the
user **at once**:
- proposed tool installs (then run only the units concerned again), including `structurizr` for
  the C4 model of §2.8 if it is missing;
- running the tests with coverage;
- **live parts**, if the app starts: performance trace (`performance-audit`), rendered SEO
  (`seo-audit`), cookies and third-party requests before consent (`gdpr-audit` §3). Results go in
  the `## Live` section of the audit file concerned;
- remaining questions.

What is declined or impossible stays "not run" in the summary.

### 2.6 Debt register

`<docs>/debt/register.md`, in the format and under the rules of `audit-deliverables` §3: create it,
or complete the existing one (`TD-xx` numbering continues). Add the Medium and higher findings of
all the audits of the pass, deduplicating: the same finding at the same place becomes one row that
cites all its sources; two distinct findings on the same file stay two rows. **Exposure** filled in
for each row (hotspot, critical path, stable code): at equal severity, the exposed one goes first.

### 2.7 Roadmap

`<docs>/debt/roadmap.md` (`audit-deliverables` §4), to create or complete, `WS-xx` workstreams in
phases:

1. **Stabilize**: secrets to rotate, critical vulnerabilities, EOL runtime, broken build or CI,
   missing backups. What is exposed today.
2. **Set up the safety net**: characterization tests on the hotspots of the critical paths, a CI
   that runs them. Nothing gets refactored before that.
3. **Refactor**: split the hotspots, break the cycles, remove confirmed dead code.
4. **Modernize**: major version upgrades, framework migrations, architecture changes.

Each workstream: goal, register rows handled (`TD-xx`), prerequisites (another workstream, a
decision), effort, risk, **done criterion** (verifiable), status "to do". The safe quick wins
raised by the audits form a separate list: at the top of phase 1 if they reduce a security or
operations risk, at the top of phase 3 otherwise (dead code, imports, small duplications).

### 2.8 C4 model

`c4-architecture` full mode (its §8), on top of the quick model, with the register of §2.6: risk
tags recomputed from the `TD-xx` rows, components (C3) of the in-scope containers that became high
risk, dynamic views of the critical paths of §2.3 (four at most; their file paths give the entry
points and the modules). Without `structurizr` (install declined in §2.5), the DSL is written and
marked not validated.

### 2.9 Summary

Complete the summary `<docs>/takeover/<YYYY-MM-DD>.md`, without copying the findings:
- scope, audits launched, run live, degraded or not run;
- the five major risks, key figures (register rows by severity, hotspots without tests);
- what is not a debt row: the "outside the code" part and the "technical audit, not legal advice"
  note from `gdpr-audit`;
- links to the audits, the register, the roadmap and the C4 model (`<docs>/architecture/`).

Commit the summary, the audits, the register, the roadmap and the C4 model:
`docs(takeover): full assessment <date>`.

## 3. Next steps (full)

Present the numbered list, then go through one step at a time: **do / skip / later**. The order
matters: the context file (§3.1) comes before the ADRs (§3.3), because `adr init` adds its pointer
to it; the tickets (§3.4) come after the prioritization (§3.2), whose order they follow. Skipped or
postponed steps are recorded in the summary `<docs>/takeover/<YYYY-MM-DD>.md`, "Next steps"
section.

### 3.1 Project context file

- Ask for the format: **`CLAUDE.md` alone**, or **`AGENTS.md`** (read by Codex, Cursor,
  Copilot…) with a one-line `CLAUDE.md` containing `@AGENTS.md` for Claude Code. If one of them
  already exists, complete it rather than creating another.
- "Nothing in the repo" mode: the file is written as a draft under `<docs>/context/`, for the user
  to copy if they wish; nothing is created in the project.
- Content per the [`context-template.md`](context-template.md) template, filled in with what the
  takeover learned, real paths under `<docs>`:
  - "Current state" points to the debt register rather than copying it; "Known issues" keeps what
    is not debt (bugs, gaps, operational traps);
  - "Refactoring goals" points to the roadmap and repeats the order chosen in §3.2 if it is
    already done, otherwise it is updated afterwards;
  - "Architecture" points to the C4 model (`<docs>/architecture/workspace.dsl` and its README) and
    keeps only a summary of a few lines.
- Any command in "Main commands" that the takeover did not run is marked "not verified". An
  existing file receives additions, never an overwrite. Committed only after validation.

### 3.2 Prioritizing the workstreams

- Rank the roadmap workstreams: severity × exposure of the `TD-xx` rows handled, then effort (at
  equal value, the cheapest first), respecting prerequisites and the phase order (nothing from
  phase 3 before the phase 2 safety net on the same code).
- Present the **top 5**, one line of reasoning each, and ask to validate or reorder.
- Write the chosen order into `<docs>/debt/roadmap.md` ("Chosen order" section, dated) and carry
  it over to "Refactoring goals" in the context file.

### 3.3 ADRs

If the `dev-workflow` plugin is installed: for each structural decision in the roadmap (dropping a
module, choice of migration), use `dev-workflow:adr`, which detects an existing register and adds
to it in the same format; no register: propose `adr init`, without imposing it. Its pointer goes
into `AGENTS.md` if that is the context file chosen in §3.1, otherwise into `CLAUDE.md`. "Nothing
in the repo" mode: new entries go into `<docs>/adr/`, with no pointer; an existing register in the
repo is read for numbering and format, but is not touched. Without the `dev-workflow` plugin, skip
this step, or list the decisions in the summary so the user can record them their own way.

### 3.4 Tickets

One ticket per workstream, in the order chosen in §3.2, as `.md` drafts in `docs/tickets/` (or the
folder given; `<docs>/tickets/` in "nothing in the repo" mode), next to the drafts written by
`living-specs:ticket-writing` if that plugin is installed. The ticket keeps the workstream
identifier from the roadmap: file `WS-<xx>-<slug>.md` (`WS-03-billing-tests.md`), the same
two-digit numbering as the `WS-xx` and `TD-xx` IDs.

Frontmatter, compatible with the one of `living-specs:ticket-writing` so that the folder index
lists them together:

```yaml
---
type: workstream
id: WS-03
title: Add characterization tests on billing
epic: EPIC-02               # Epic of the phase if it has one, empty otherwise
status: draft               # draft | ready (ticket status, not the workstream status)
updated: YYYY-MM-DD
platform_type: <to ask>
---
```

- **Index**: `README.md` of the ticket folder chosen above (`docs/tickets/README.md` by default,
  `<docs>/tickets/README.md` in "nothing in the repo" mode; same format as
  `living-specs:ticket-writing` if installed, otherwise a simple table: ID, type, title, status,
  file): one line per workstream ticket, type `workstream`, created with the first ticket if it is
  missing.
- **Phase Epic**: a roadmap phase can become an Epic (`EPIC-xx`, Epic template of
  `living-specs:ticket-writing` if installed, its exit conditions taken from the done criteria of
  its workstreams). The tickets of its workstreams then carry `epic: EPIC-xx`, and the phase, in
  the roadmap, cites its Epic.
- A workstream has no template in `ticket-writing`: use the body below.
- The ticket status (draft, ready) does not replace the workstream status (to do, in progress,
  done), kept in the roadmap. A workstream ticket moves to `ready` when the goal, the `TD-xx`
  handled, the prerequisites and the done criterion are filled in and the user has validated them;
  before that, it stays `draft`.

No access to a ticketing platform (Jira, Linear, Notion…), MCP included: writing is kept separate
from publishing, which happens outside this skill. The type to use on the platform is recorded in
`platform_type:`, to ask the user: a type dedicated to technical debt if the project's platform has
one, otherwise the one they choose. Not Task, which `ticket-writing` reserves for investigations.

Body of a workstream ticket:

```markdown
**Goal**
<what the workstream changes, in one or two sentences>

**Debt handled**
TD-xx, TD-yy (register: <docs>/debt/register.md)

**Prerequisites**
<workstreams or decisions to do first>

**Done criterion**
<verifiable>

**Effort / risk**
<S/M/L> / <regression risk>
```

### 3.5 Starting the first workstream

Propose how to tackle the first workstream in the chosen order, without doing it:
- quick wins or dead code → `maintainability-audit` invoked alone (§11) on the findings concerned;
- secrets, vulnerabilities, config → `security-audit` invoked alone;
- characterization tests → a dedicated session, on a separate branch, starting from the done
  criterion;
- version upgrade or migration → `maintenance` zone `deps` or `build`, or an ADR first if the
  decision is not made.

Then checkpoint in `HANDOVER.md`, and suggest `/clear` before starting: what follows is a new
topic, and everything needed is in the reports.

## 4. Resuming across sessions

A full run on a large project can span several sessions. Checkpoint in `HANDOVER.md` (with
`dev-workflow:handover` if the `dev-workflow` plugin is installed; otherwise skip): mode, `<docs>`,
branch, scope, audit units returned and remaining, current step (collection follow-ups, register,
roadmap, next steps done, skipped or postponed).
