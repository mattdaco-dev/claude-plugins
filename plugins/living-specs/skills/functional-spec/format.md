# The living-specs format (v1)

Shared reference for `functional-spec`, `screen-spec`, `retro-spec`, `ticket-writing` and the
plugin's SessionStart hook.

A lightweight functional and screen specification in Markdown, kept up to date at every working
session: no gates, no agent roles, no scripts. Every element is found by its identifier.

## 1. Tree

```
docs/glossary.md                 business glossary, mandatory (glossary skill), outside docs/specs/
docs/glossary-<domain>.md        if it is split by domain (glossary skill, section 6)
docs/specs/
├── README.md                    marker, product, roles, index of features and screens
├── domain-model.md              business objects, relations, lifecycles
├── questions.md                 questions Q-xxx, open and answered
├── features/<slug>.md           one sheet per feature (the size of an Epic)
└── screens/
    ├── SC-xx-<slug>.md          one sheet per screen
    └── screenshots/SC-xx-<state>.png     SC-xx-<state>-<value>.png for a setting variant
```

`features/` and `screens/` are created only with their first file (git does not keep an empty
folder). Slugs are lowercase with hyphens, in the language of the business documents (they name
business things). Screenshot state names are fixed: `nominal`, `loading`, `error`, `empty`,
`no-access`.

Templates: `templates/` in this skill for the README, the domain model, the questions and a
feature; `../screen-spec/screen-template.md` for a screen. Always start from the template.

In this format, "the glossary" means `docs/glossary.md` and, if it is split by domain, every
`docs/glossary-<domain>.md`; `docs/glossary.md` then stays as the index (list of files per domain,
cross-domain terms). All of them are read, and a term is defined in one file only.

**Additions allowed to the template.** A spec produced by `retro-spec` may also carry:

- in the README, a **Criticality** column (Critical, High, Med, Low) in the features table, and the
  sections **Coverage and doc/code drift**, **External integrations**, **Cross-cutting
  non-functional requirements** (those of a single feature go in its sheet);
- at the end of a feature sheet, a **Key files** section (`path:line`).

Any project may also add the External integrations and Cross-cutting non-functional requirements
sections to the README. Once present, these additions are kept up to date like the rest; no other
departure from the template.

### Language

Write the content (statements, messages, definitions, descriptions, slugs) in the language the user
works in. What other skills and tools look for stays exactly as defined here, whatever that
language: identifiers and their prefixes, file and folder names, the format marker, frontmatter keys
and values, status values, and the section headings and column names of the templates.

## 2. Markers

The `README.md` starts with:

```yaml
---
format: living-specs
version: 1
---
```

This is what the skills and the SessionStart hook read. A `docs/specs/` without this marker is out
of format (for example an older free-form `retro-spec` output).

After a move (section 7), the original repository keeps only `docs/specs/README.md` with
`moved_to: <repository or URL>` instead of `format:`: nothing is fed there any more, and the
migration is not offered again.

A project that declines the format records it in `CLAUDE.local.md` (not versioned, nothing imposed
on the team): `living-specs: declined`. Before writing the line, check that the file is ignored by
git (`git check-ignore -q CLAUDE.local.md`); otherwise add it to `.git/info/exclude`, which stays
local. The line is also read in `CLAUDE.md` and `.claude/CLAUDE.md`.

## 3. Identifiers

| Prefix | Means | Defined in |
|---|---|---|
| `UF-xx` | user flow | feature sheet |
| `BR-xx` | business rule | feature sheet |
| `CALC-xx` | calculation | feature sheet |
| `MSG-xx` | functional message (notification, email, business feedback) | feature sheet |
| `SC-xx` | screen | `screens/SC-xx-<slug>.md` |
| `SC-xx-<name>` | dialog of a screen (no `SC` of its own) | sheet of its screen |
| `MSG-Uxx` | interface message (empty, technical error, access denied) | screen sheet |
| `Q-xxx` | open question | `questions.md` |

- **Numbering is global to the project, per prefix**: `BR-14` is unique across all of
  `docs/specs/`, and the same goes for `MSG-Uxx` across all screen sheets. Next number = highest
  existing number for the prefix + 1, obsolete ones included
  (`grep -rhoE 'BR-[0-9]+' docs/specs | sort -t- -k2 -n | tail -1`, `MSG-U[0-9]+` for interface
  messages).
- **Stable once on the default branch**: it never changes and is never reassigned. On a branch not
  merged yet, check the highest number on the default branch before merging and renumber the new
  identifiers of the branch if they collide.
- **Plain Markdown, no HTML**: no anchor added by hand. An element that has a heading carries its
  identifier at the start of that heading (`# SC-03 …`, `### UF-01 …`, `### CALC-01 …`,
  `### SC-03-cancellation …`): that is its anchor, the one the Markdown renderer generates. An
  element in a table row (`BR`, `MSG`, `MSG-U`, `Q`) has its identifier in the first column. A
  permission has no identifier: it is found by the action in the first column of the permissions
  table. Either way, the element is found by its identifier or its action (search or `grep`).
- **Citation**: the bare identifier within the same file; from another file, a link to the file
  that defines it: `[BR-14](../features/booking.md)`.
- A feature has no identifier: its slug is enough.

## 4. Statuses

**Rule, calculation, message (functional `MSG-xx` and interface `MSG-Uxx`), permission, business
object**: a Status column and a Source column (for a calculation, written as a list: Status and
Source lines).

| Status | Meaning |
|---|---|
| Proposed | statement not accepted yet: inferred from the code or an existing doc, or written by Claude from a user decision without the user having seen and accepted this statement yet |
| Validated | statement dictated by the user, or shown to the user and accepted as is; it is authoritative |
| Obsolete | dropped: text struck through (`~~…~~`), reason and date in Source; the row stays |

- **A rule mentioned without being settled is not a rule**: it becomes a question `Q-xxx`
  (section 5), never a Proposed row. Proposed is only for a statement whose substance is
  established (code, doc, user decision) and whose wording awaits the user's agreement.
- Validation applies to the **statement**: a decision settled in a grill-me or an accepted
  recommendation does not validate the statement Claude derives from it until Claude has shown it
  and the user has accepted it.
- A blanket agreement ("ok, go ahead" on an answer that contains several rules among other things)
  validates nothing. A list of statements explicitly presented for validation, and explicitly
  accepted ("BR-03 to BR-07 ok"), validates them.
- A Validated rule is rewritten only with the user's words. Any other change makes it Obsolete and
  creates a new rule, Proposed, to be accepted.
- An obsolete calculation has its heading struck through, reason and date in Source.

**Question**: `open` or `answered`.

**Sheet** (feature or screen): `status` in its frontmatter, `draft`, `in review` or `validated`.
Moving to `validated` happens at the user's request. Any change to a validated sheet sends it back
to `in review`. The status in the README table follows the sheet's.

## 5. Writing rules

- **One rule, one declarative sentence**, testable without reading the rest: "A booking that has
  started can no longer be cancelled", not "the system must check that…".
- **Each rule has a source**: `grill-me 2026-10-12`, `discussion 2026-10-14`, `Q-003`, `proto v3`,
  `code src/x.ts:42 [observed]`, `doc <file>`, regulation.
- **No invented business rule**, not even as Proposed. What is missing, what the user mentions
  without settling, or what Claude recommends without it being settled, becomes a question `Q-xxx`
  with the working assumption, cited where it applies. Never a bare `[?]`.
- **Messages word for word**, variable parts between angle brackets: "Booking <room> on <date> is
  cancelled".
- **Business, not physical**: no tables, keys or SQL types.
- **Behavior stated positively**: "the button is disabled until…".
- **Roles, never people**; example data is fictitious.
- **Glossary mandatory**: `docs/glossary.md`, index of the per-domain files if it is split
  (section 1; `glossary` skill), created if missing, enriched with each business term met. Its
  terms are used word for word, never a synonym from its "Not to be confused with" column.
- The feature/screens link is authoritative in the frontmatter (`screens:` of a feature,
  `features:` of a screen); the Screens column of the rules table says which screens apply each
  rule.

## 6. Screens: target or existing

A screen sheet describes the **target** screen when designing (prototype), the **existing** screen
when `retro-spec` documents an application. In that case:

- "Prototype gaps" reads "not applicable";
- `prototype:` is `not applicable`, the application route goes in Access (Entry);
- as long as no screenshot has been taken: `screenshots_taken:` empty, no image under the heading,
  "no screenshot" in the Screenshot column of States. Screenshots taken later on the running
  application (`screen-spec` section 4) are dated
  `screenshots_taken: YYYY-MM-DD (app <version or commit>)`.

## 7. Where the specs live

In the repository where the design happens: the prototype, or the project itself. When development
of the real application starts in another repository, `docs/specs/` **moves** there: full copy,
then on the prototype side only the README remains, reduced to the `moved_to:` marker (section 2),
plus a link in the prototype's root README. A single live copy.
