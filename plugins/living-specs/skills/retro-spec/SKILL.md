---
name: retro-spec
description: Generates a retroactive spec of an existing project (no specs or partial specs), covering product and roles, features and criticality, flows, business rules, screens, domain model, integrations, non-functional requirements. Inferred from the code with assumptions flagged, written in docs/specs/ in the living-specs format (the migration tool to that format). Use when the user wants to reverse-engineer specs from code, or says "retro-spec", "reverse spec", "generate a spec of the project", "spec from the code", "document the existing code as a spec", "rétro-spec", "spec de l'existant".
---

Goal: produce a **living spec of what exists** in `docs/specs/`, in the living-specs format defined
in the `format.md` of the `functional-spec` skill
([`../functional-spec/format.md`](../functional-spec/format.md), to read before writing). It
documents the product as it is built and serves as the basis for future development. Inferred from
the code, **assumptions and uncertainties flagged**: a committable draft that is iterated on
afterwards. Read-only first, then the spec files are written. **Never `git push`.**

Write the content in the language the user works in; what `format.md` section 1 (Language) fixes
stays as defined.

## Guiding principle: epistemic honesty

The code gives the *what* and the *how*, not the *why*. So:

- Tag every non-trivial statement: **`[observed]`** (read in the code), **`[inferred]`**
  (deduced), **`[?]`** (unknown, to be confirmed).
- **Never pass an inference off as a fact.** The product and the framing will be largely
  `[inferred]`: own it.
- In the format: the tag goes into the rule's **Source** column (`code src/x.ts:42 [observed]`);
  a rule taken from the code is **Proposed** until the user has accepted its statement; a `[?]`
  becomes a question `Q-xxx` in `docs/specs/questions.md`, cited in the Questions section of the
  sheet, never a rule.

## 0. Scope

- `retro-spec` alone: **whole project**.
- `retro-spec <area>`: one feature or a targeted area (e.g. `retro-spec invoicing`).

## 1. Locate the project

As in `functional-spec` section 1, the first line that applies decides:

| Situation | Next |
|---|---|
| `living-specs: declined` in `CLAUDE.local.md`, `CLAUDE.md` or `.claude/CLAUDE.md` | this skill only writes in this format: report it, and continue only if the user lifts the decline (removes the line) |
| `docs/specs/README.md` with `moved_to:` | the specs live in the repository indicated: say so, write nothing here; the retro-spec is done in that repository |
| `docs/specs/README.md` with `format: living-specs` | complete the existing spec (section 6, merge), without touching Validated elements |
| `docs/specs/` without the marker, or another spec document | migration: what exists is converted to the format (section 6) |
| nothing | generate the spec |

## 2. Preamble

1. **Context**: if a `HANDOVER.md` exists at the root, read it (the `dev-workflow:handover` skill
   maintains it, if the dev-workflow plugin is installed).
2. **Stack**: read the manifests (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.)
   to adapt the analysis.
3. **Take in what exists** (source of truth): `README`, `docs/`, ADRs or `DECISIONS.md`,
   meaningful comments, an existing `docs/specs/`, the glossary (`docs/glossary*.md`). Treat it as
   the **reference intent**: don't overwrite it, complete it, and **report doc/code drift** (the
   doc says X, the code does Y).
4. **Dedicated branch**: before the first commit, create or join `docs/specs-retro`
   (`docs/specs-retro-<area>` for an area), on the model of `functional-spec`'s
   `docs/specs-<slug>`. Read-only collection can happen before branching.

## 3. Phase 1: overall map (read-only)

Map: entry points, routes and endpoints, modules and packages, data models and migrations,
dependencies and external integrations, configuration and environment variables, tests.
**Derive the list of features** from it, **product**-oriented, not technical layers.

**Multi-signal criticality** per feature: rating **Critical / High / Med / Low** and a short
justification, crossing:

- business stakes (authentication, payment, sensitive data, main flow);
- technical centrality (most depended-on or referenced modules);
- entry points and main routes;
- test coverage;
- change frequency (git history).

Produce a **coverage map**: for each feature, *already documented / inferred / missing*, with the
doc/code drift spotted.

## 4. Adaptive checkpoint

- **Small project, clear list**: go straight on.
- **Big or ambiguous**: present the **list of features and their criticality** (with the coverage
  map) for a quick validation **before** the detailed analysis, and adjust the split based on the
  feedback.

## 5. Phase 2: detailed analysis (read-only)

One analysis per feature. When there are several, **offer** to hand them to `analyst` agents
(read-only) running in parallel, one per feature: announce the split (how many agents, what each
does and returns), wait for the user's agreement, then launch them all in a single message so they
run at the same time. Each agent's brief gives the project path, the feature and its entry points
(phase 1 map), the existing specs or docs to treat as source of truth, and the list of headings
below. Without agreement, run the analyses in sequence. Each analysis returns, structured:

- **behavior**: main flow and edge cases observed;
- **business rules**: each constraint, condition or prohibition observed, one declarative sentence
  each, tagged `[observed]` or `[inferred]` with `path:line`;
- **flows**: end-to-end sequences of actions (future `UF-xx`);
- **screens** (if there is a front end): pages or routes, data displayed, actions, states handled
  (future `SC-xx`);
- **business objects and data** touched, external **integrations**, **roles and permissions**
  concerned;
- **assumptions and open questions**;
- **key files** (`path:line`).

During this phase: **change nothing**.

## 6. Writing into `docs/specs/`

Tree, identifiers and templates of the format (`format.md`, templates of `functional-spec` and
`screen-spec`). The additions specific to a retro-spec (Criticality column, README sections, Key
files) are those that `format.md` section 1 allows, no others.

- `README.md` (with the marker): product `[inferred]`, roles, index of features with the
  **Criticality** column, index of screens, link to the glossary; sections **Coverage and doc/code
  drift**, **External integrations**, **Cross-cutting non-functional requirements** (those of a
  single feature go in its sheet);
- `features/<slug>.md`: one sheet per feature, rules `BR-xx` (status Proposed, source with tag and
  `path:line`), flows `UF-xx`, roles and permissions, **Key files** section at the end of the sheet;
- `screens/SC-xx-<slug>.md` if there is a front end: one sheet per page or route, describing the
  **existing** screen, without screenshots, per `format.md` section 6 ("Prototype gaps" and
  `prototype:` set to `not applicable`, route in Access, `screenshots_taken:` empty, no image under
  the heading). Screenshots come later from the running application, on request (`screen-spec`
  section 4, "Without proto-bar or route");
- `domain-model.md`: the objects seen from the business side, their relations and lifecycles,
  without tables, keys or SQL types (`format.md` section 5); what the data schema has that is
  purely technical stays out;
- `questions.md`: all the `[?]`;
- **the glossary, mandatory** (`glossary` skill): the business vocabulary met in the code, the docs
  and the interface, definitions as Proposed with their source, misleading names in "Not to be
  confused with"; if it already exists, complete it without overwriting Validated entries.

Global numbering, in the order of features by decreasing criticality. If a spec or a doc already
exists: **merge without overwriting**. What exists is the reference (a rule taken from a doc is
Proposed with the doc as source, unless it was already Validated in this format; what the doc leaves
open becomes a question), what is missing is added, the drift is reported in the Coverage and drift
section. An older free-form `retro-spec` output (a `docs/specs/` without the marker) is converted to
this format.

## 7. Commit the generation

**One commit** on the branch: `docs(specs): generate initial retro-spec`. **No push**: the user
reviews the branch, then merges and pushes.

Then offer a review by the `reviewer` agent, without launching it, and the validation of the
statements by the user over the sessions (`functional-spec` section 4).

## 8. Cleaning up superseded docs (approval required)

Once the spec is written and committed, **the new spec is authoritative**. Docs that became obsolete
are cleaned up, **only after** their useful content has been taken into `docs/specs/`, and **never
silently**.

1. **Classify** the existing docs, with the reason:
   - **To delete**: docs and specs now covered by the new spec (partial specs, outdated design
     notes, stray spec files).
   - **To merge**: content still useful not yet integrated. **Move it into the spec first**, then
     delete the source.
   - **To keep**: everything else.
2. **Careful scope**: **never** delete `LICENSE`, `CONTRIBUTING`, ADRs or `DECISIONS.md`,
   `CHANGELOG`, operations runbooks, API reference, unless the content is clearly taken over **and**
   explicitly approved.
3. **README**: update it **in place** (fix what is partial or outdated), keep its role as the shop
   window (presentation, installation, getting started, usage) and add a **link to `docs/specs/`**
   for the details. Don't merge the spec into the README.
4. **Present the cleanup plan** (list classified *to delete / to merge / to keep*, with the reason)
   and **wait for a block approval** before executing.
5. **Execute**: `git rm` of the approved files (reversible thanks to the branch) and README update.
   **One** dedicated commit: `docs: remove docs superseded by the specs and update README`.
   **No push.**

## 9. Resuming from one session to the next

A big project can spread over several sessions. **Keep a resume point up to date as you go**:
features mapped, analysed, remaining, decisions pending. If the dev-workflow plugin is installed,
keep it in `HANDOVER.md` with the `dev-workflow:handover` skill; otherwise in a local notes file
the user agrees on, not committed.

## 10. Do the best with what is accessible

If a tool is not accessible (e.g. `git log` for change frequency), **carry on without it** and
**note it**; never invent, nor pass an estimate off as a verification.
