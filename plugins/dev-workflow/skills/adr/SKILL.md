---
name: adr
description: Keeps an architecture decision log (ADR) for a project, one file per decision in a light format (Context, Decision, Rationale, Consequences). Detects an existing register (docs/adr/, doc/adr/, adr/, docs/decisions/, .adr-dir, DECISIONS.md...) and reuses it, otherwise creates one on request, then adds and evolves entries when a structural decision is made. Without a register or a request, does nothing (folders in plain "cowork" mode). Use when the user wants to record an architecture or tech decision, set up a decision log, or says "/adr", "adr", "decision log", "record this decision", "document this choice", "consigne cette décision", "journal de décisions", "on documente ce choix".
---

Goal: keep a **decision log** (ADR, Architecture Decision Records) for a project, with **one file
per decision**, in the light **Context, Decision, Rationale, Consequences** format. Two phases:
**bootstrap** of the register (switch to "project mode"), then **ongoing upkeep** (record
structural decisions as they are made). **Never `git push`**: the user pushes.

Write ADRs in the language the user works in, or in the language of the existing register.

## 0. Project mode or cowork mode (the principle that governs everything)

- **Project mode** = a register exists (section 1): keep it up to date, each structural decision
  gets an entry.
- **Cowork mode** = no register: do **nothing** (no noise, no cost). You may *suggest* the init if
  a real architecture decision comes up, without forcing it.
- The switch to project mode happens **once**, through `adr init` (or when the user asks to
  document a choice). The upkeep instruction lives in the **project's context file** (pointer added
  at bootstrap, section 3), so it is only active in that project.

## 1. Detect an existing register

Before creating anything, search the project in this order:

1. `.adr-dir` at the root (adr-tools): it holds the register path;
2. the usual folders: `docs/adr/`, `doc/adr/`, `adr/`, `docs/decisions/`,
   `docs/architecture/decisions/`;
3. failing that, numbered files elsewhere (`**/[0-9][0-9][0-9]*-*.md` whose title starts with
   `ADR` or whose body has a status and a decision section, MADR format included);
4. a single `DECISIONS.md` file (or `docs/DECISIONS.md`) that concatenates the decisions.

A register found is **reused as is**: its folder, its file format (MADR, Nygard, adr-tools...), its
numbering (width and prefix: `0001-`, `ADR-001`...), its index if it has one, its language. Never
create a second register next to it. Several registers found: ask which one is authoritative.

Below, `<register>` means the chosen folder; `docs/adr/` is only the default for a register
created by this skill.

## 2. Scope and invocation

- `adr init`: bootstrap the register in the current project (section 3).
- `adr add [title]`: add a decision with the next number (section 4).
- `adr supersede <number> [title]`: new decision that replaces the given one (section 5).
- `adr` alone: without a register, suggest the init; with a register, list the state and suggest
  adding one.

**Called by `code-audits:legacy-takeover` in "nothing in the repo" mode** (if the code-audits
plugin is installed): the root is `<docs>` (path given by the user, often outside the repo). New
entries go to `<docs>/adr/`, no pointer is written in the project, nothing is committed. If the
repo already has a register (section 1), it is **read** for numbering (continue after its highest
number) and for format (template, prefix, language), but it is **not touched**: no new entry, no
index update, no status change on any of its decisions (a replacement is noted in the new entry of
`<docs>/adr/`).

## 3. Bootstrap (`adr init`)

1. **Check** nothing gets overwritten: if a register exists (section 1), do not re-initialise,
   switch to `add`.
2. **Create** `docs/adr/` and its index `docs/adr/README.md` (table: number, title, status, date).
3. **Project pointer**: a short section in the project's context file.
   - Where: in `AGENTS.md` if it exists or if it is the chosen context file (a `CLAUDE.md` reduced
     to `@AGENTS.md`); otherwise in `CLAUDE.md`.
   - Neither exists: ask whether to create `CLAUDE.md`, create `AGENTS.md`, or go without a
     pointer. Never create a context file without agreement.
   - Content:
     > ## Decisions
     > This project keeps a decision log in `<register>`. Record every **structural decision**
     > (new entry through the `adr` skill) and update the index.
4. **First entry**: suggest an ADR recording the adoption of the log itself (useful as a format
   example), without forcing it.
5. **Git**: do not commit on the default branch, create a branch first if needed; one commit
   `docs(adr): bootstrap decision log`; **no push**.

## 4. Add a decision (`adr add`)

1. **No duplicate**: search the register for a decision on the same subject.
   - It exists and the new decision says something else: replace it (section 5).
   - It exists and says the same thing: add nothing, cite it.
2. **Number**: highest existing number + 1, in the register's format (section 1). Register created
   by this skill: `NNNN` on 4 digits, file `docs/adr/NNNN-title-in-kebab-case.md`.
3. **Short interview** if information is missing: what choice, why, which alternatives were
   rejected, what consequences. Do not invent; an uncertain point is marked `[to confirm]`.
4. **Write** the ADR with the register's template, or the one in section 6 for a register created
   here. Status `Accepted` if the decision is made, `Proposed` if it awaits a call.
5. **Update** the register's index if it has one.
6. **Git**: one commit `docs(adr): <number> <short title>`, **no push**.

## 5. Evolve a decision

ADRs are **immutable** once accepted: history is not rewritten. Only the status, its date and the
links between ADRs change; the index follows each time.

- **Proposed to Accepted**: when the user decides. While an ADR is `Proposed`, its content may
  still change; when it moves to `Accepted`, set today's date.
- **Proposed rejected**: status `Rejected`, with one line saying why. The file stays.
- **Replacement** (`adr supersede`): create a new ADR (`Accepted`) whose header says
  `Supersedes: <number>`, and set the old one to `Superseded by: <new number>`.
- **Deprecated**: the decision no longer applies and nothing replaces it (module removed,
  constraint gone). Status `Deprecated` with the date and one line of reason.

## 6. ADR template (register created by this skill)

Minimal header and the four sections. Statuses: `Proposed`, `Accepted`, `Rejected`, `Superseded`,
`Deprecated`.

```markdown
# ADR-NNNN: <title>

- **Status**: Accepted
- **Date**: <YYYY-MM-DD>
- **Supersedes / Superseded by**: (if any)

## Context
The problem, the constraints, what forced a choice.

## Decision
What was decided, stated affirmatively and without ambiguity.

## Rationale
Why this option; **alternatives considered** and why they were rejected.

## Consequences
What it implies (positive AND negative): debt, new constraints, follow-ups to plan.
```

The index `docs/adr/README.md`:

```markdown
# Decision log (ADR)
| # | Title | Status | Date |
|---|-------|--------|------|
| [0001](0001-adopt-the-adr-log.md) | Adopt the ADR log | Accepted | <date> |
```

## 7. What to record (and what NOT to, to avoid noise)

**Record** a *structural and lasting* decision: choice of technology, framework or major library,
architecture style, module split, public API contract, data model, auth or security strategy,
cross-cutting convention, accepted trade-off, abandonment or deprecation of an approach.

**Do not record**: trivial implementation details, reversible choices with no cost, style
preferences already covered by project instructions or a linter, code TODOs, what belongs in a
commit message. When in doubt: "would a newcomer to the project need to know the *why* of this
choice?" If not, no ADR.

## 8. Single file

A project that keeps its decisions in a single `DECISIONS.md` (concatenated file) keeps it: add
entries in the same place, with the same format and numbering, without forcing a migration to a
folder.

## 9. Guardrails

- **Never rewrite an accepted ADR**: only its status evolves (section 5).
- **One register**: reuse the existing one (section 1).
- **Numbering**: never reuse a number, even after a deletion.
- **No push**; Conventional Commits; branch before the first commit when on the default branch.
- **Respect cowork mode**: without a register and without a request, create nothing on your own
  initiative, neither a register nor a context file.
