---
name: functional-spec
description: Writes and maintains a project's functional specs in docs/specs/ in the living-specs format (one sheet per feature, user flows UF-xx, business rules BR-xx, calculations, messages, roles and permissions, AI assistance, abuse and limits, domain model, questions Q-xxx). Use after a grill-me on a new project or feature, when migrating a project to this format, or when the user says "functional spec", "write the spec", "business rules", "update the spec", "formalize the specs", "spec fonctionnelle", "règles de gestion", "mets à jour la spec". For screens, see screen-spec.
---

# Functional spec

The functional spec says **how the product behaves**, independently of screens and technology:
flows, rules, business objects, permissions. It is the reference for the `BR-xx` that screens,
tickets and tests cite.

The format (tree, markers, identifiers, statuses, writing rules, language) is in
[`format.md`](format.md). Read it before any writing.

## 1. Locate the project

In this order, the first line that applies decides:

| Situation | Next |
|---|---|
| `living-specs: declined` in `CLAUDE.local.md`, `CLAUDE.md` or `.claude/CLAUDE.md` | do nothing, don't offer again, unless explicitly asked |
| `docs/specs/README.md` with `moved_to:` | the specs live elsewhere: say so, write nothing here |
| `docs/specs/README.md` with `format: living-specs` | project in living specs: section 3 or 4 |
| `docs/specs/` without the marker, or another spec document | out of format: offer the migration (section 5); on explicit invocation, migrate directly |
| nothing, and application code that already carries features | on explicit invocation or after an accepted grill-me: ask (`AskUserQuestion`) between `retro-spec` first (spec of the existing code, recommended) and an empty spec limited to the new work (section 2, the existing code stays to be retro-specified); otherwise offer (section 5) |
| nothing, no application code (new project, prototype) | on explicit invocation or after an accepted grill-me: section 2; otherwise offer (section 5) |

Out of scope altogether: a tooling or configuration repository (dotfiles, Claude Code config,
plugin repository) and a working folder with no application project (notes, documents, one-off
exchanges).

Branch: spec files are committed with the work that creates them, on that work's branch. A spec on
its own goes on `docs/specs-<slug>`. On the default branch, offer to create a branch before the
first commit. Never push: the user pushes.

## 2. Initialize

1. Copy the templates `README.md`, `domain-model.md`, `questions.md` from `templates/` into
   `docs/specs/`. Replace `PROJECT_NAME`, fill in Product and Roles with what is known.
   Glossary missing (`docs/glossary*.md`, `format.md` section 1): create it (`glossary` skill) with
   the terms already known.
2. Go on to section 3. `features/` and `screens/` are created with their first file.

## 3. Formalize a feature (after the grill-me)

Inputs: the grill-me decision summary, or the exchange that stands for it. On a project already in
living specs, this is where the spec gets written, at the end of the grill-me, in one block: nothing
while the questions are being asked.

1. Copy `templates/feature.md` to `docs/specs/features/<slug>.md`. Slug named after the feature as
   the business calls it (`fee-management`). Feature already described: complete its sheet.
2. Distribute the decisions:
   - **Need**: goal, actors, scope and out of scope;
   - **User flows** `UF-xx`: one per sequence of actions an actor carries out end to end;
   - **Business rules** `BR-xx`: each constraint, condition or prohibition, one sentence each;
   - **Calculations**, **Messages**, **Roles and permissions** when the discussion settled them;
   - **AI assistance**: each AI track settled during the grill-me (`grill-me`, "AI track"), kept
     or dropped with its reason; a kept track gives its `BR-xx` (behavior, human validation, data
     sent, fallback when the AI fails). No track discussed: the question "what can AI do here?"
     goes into `questions.md`, the section never stays empty;
   - **Abuse and limits**: each abuse settled during the grill-me (`grill-me`, "abuse track",
     grid in `abuse.md` section 3), controlled or accepted with its reason; a control gives its
     `BR-xx` and the `MSG-xx` shown when the limit is hit (`abuse.md` section 4). An unsettled
     figure is a question. Nothing discussed: the question "how could this feature be misused?"
     goes into `questions.md`, the section never stays empty;
   - business objects, attributes and statuses in `domain-model.md`.
3. Statuses (`format.md` section 4): only a decision settled by the user, or whose recommendation
   they accepted question by question, becomes an element (rule, calculation, message,
   permission). Its statement, written by me, enters as **Proposed**; it is **Validated** only once
   shown and accepted (step 6), unless it repeats word for word what the user said. Source:
   `grill-me YYYY-MM-DD`.
4. What the grill-me left open, what the user mentioned without settling, and what I recommend
   without it being settled, becomes a line in `questions.md` (with the working assumption) and a
   link in the Questions section of the sheet. Never a Proposed rule.
5. Update the README (feature row, new roles) and the glossary: each business term set during the
   grill-me, Validated if the user dictated the definition or accepted it as is after seeing it,
   Proposed otherwise (`glossary` skill, section 4).
6. Give a short recap: sheet created, number of UF, of BR, open questions, then the list of
   Proposed statements to validate. Move to Validated the ones the user explicitly accepts, rewrite
   the ones they correct with their words (Validated too). Offer a review by the `reviewer` agent,
   without launching it.

## 4. Keep it up to date

On a project in living specs, this part applies **without asking** (the plugin's SessionStart hook
reminds it at the start of each session). A functional decision made in the exchange (rule, edge
case, permission, message, calculation, business object) goes into its sheet as it happens, and a
new business term into the glossary:

- **new rule**: next number (`format.md` section 3). Validated only if the user stated it, or if I
  showed them the statement and they accepted it (`format.md` section 4). Settled decision whose
  statement I write: Proposed, statement shown in the answer for the user to accept. Rule mentioned
  without being settled, assumption or recommendation of mine: a question, not a rule. Source
  `discussion YYYY-MM-DD` or `proto vN`;
- **Proposed rule changed**: rewrite the statement, update the source;
- **Validated rule changed**: only with the user's words; otherwise the old one becomes Obsolete and
  a new one is created, Proposed;
- **rule dropped**: Obsolete, struck through, reason and date; never deleted;
- **answer to a question**: record it in `questions.md` (status answered), then update what it
  unblocks;
- `updated` in the frontmatter set to today's date; a `validated` sheet goes back to `in review`,
  and the README is aligned.

An idea thrown in passing is not a decision: nothing, or a question. At the end of the answer, one
line says what moved ("Specs: BR-12 added (proposed), BR-04 obsolete"); no line if nothing moved.

While a grill-me is running, nothing is written: the spec is formalized at the end (section 3).

## 5. Offer the migration

A single offer per session, with `AskUserQuestion`:

- **Migrate**:
  - project with code and no spec: `retro-spec`, which writes in this format;
  - existing specs (older free-form `retro-spec` output, in-house doc, pasted text): convert. Each
    rule established by the doc gets a `BR-xx` as Proposed with the doc as source; what stays open
    or vague there, and content that cannot be classified, becomes a question. Report the doc/code
    drift spotted. The old files are deleted once their content has been taken over, after the
    deletion plan is approved;
  - project with neither code nor spec: section 2.
- **Not now**: record nothing; the question will come back in a later session.
- **Never**: add `living-specs: declined` to `CLAUDE.local.md`, after checking it is ignored by git
  (`format.md` section 2), and don't offer again.

## 6. Check

Before handing over a sheet, or on request:

- each `BR-xx`, `CALC-xx`, `MSG-xx`, `MSG-Uxx`, permission and business object has a source and a
  status; no number reused, no duplicate;
- each citation to another file is a link to the file that defines the identifier;
- each cited question exists in `questions.md`, each open question is cited somewhere;
- the screens in the frontmatter exist or are announced in the README;
- the AI assistance section has at least one track or points to an open question; each kept track
  has its three guardrails and its `BR-xx`, each dropped track its reason;
- the Abuse and limits section has at least one line, an argued absence of surface or an open
  question; each controlled abuse cites its `BR-xx` (and its `MSG-xx` if the user sees the limit),
  each accepted abuse its reason;
- the business terms used are in the glossary (`docs/glossary*.md`), no synonym to avoid;
- each Proposed statement is waiting for a validation that has been requested; no rule mentioned
  without being settled has been written as a rule;
- no bare `[?]`, no real person, no real data.
