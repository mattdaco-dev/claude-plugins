# living-specs

A Claude Code plugin that grills a feature with you, then keeps the project's functional specs,
screen specs, business glossary and tickets in sync with the work, session after session.

The specs are plain Markdown in the repository. They are "living": every functional decision made
in a session, and every screen changed in the prototype, updates its sheet as it happens, without a
separate documentation pass. A statement Claude writes stays **Proposed** until you have seen and
accepted it; only then is it **Validated**. Anything mentioned but not settled becomes an open
question, never a rule.

## Install

```
/plugin marketplace add mattdaco-dev/claude-plugins
/plugin install living-specs@mattdaco
```

## What it maintains

```
docs/glossary.md                 business glossary (or an index of docs/glossary-<domain>.md files)
docs/specs/
├── README.md                    format marker, product, roles, index of features and screens
├── domain-model.md              business objects, relations, lifecycles
├── questions.md                 open and answered questions
├── features/<slug>.md           one sheet per feature
└── screens/
    ├── SC-xx-<slug>.md          one sheet per screen
    └── screenshots/             one screenshot per screen state (SC-xx-<state>.png)
docs/tickets/                    Epic, user story and Task drafts, with an index
```

`docs/specs/README.md` starts with the marker `format: living-specs`; that is how the skills and
hooks recognise a project in this format. Content is written in the language you work in; IDs, file
names, frontmatter keys, statuses and template headings stay as defined.

## Identifiers

| ID | Means | Defined in |
|---|---|---|
| `UF-xx` | user flow | feature sheet |
| `BR-xx` | business rule | feature sheet |
| `CALC-xx` | calculation | feature sheet |
| `MSG-xx` | functional message (notification, email) | feature sheet |
| `SC-xx` | screen (`SC-xx-<name>` for one of its dialogs) | `screens/SC-xx-<slug>.md` |
| `MSG-Uxx` | interface message (empty, error, access denied) | screen sheet |
| `Q-xxx` | open question | `questions.md` |
| `EPIC-xx`, `US-xxx`, `TA-xxx` | ticket drafts | `docs/tickets/` |

Numbering is global to the project per prefix, and an ID never changes once on the default branch.

## Skills

- `grill-me`: interviews you one question at a time until every branch of a plan is settled,
  including an AI track and an abuse track on each feature, then hands off to the specs and glossary.
- `functional-spec`: writes and maintains the feature sheets, domain model and questions; owns the
  format reference (`format.md`) and the abuse grid (`abuse.md`).
- `screen-spec`: one sheet per screen (content, actions, five states, interface messages,
  navigation) with screenshots of the HTML prototype.
- `glossary`: creates and maintains `docs/glossary.md`, with Proposed/Validated statuses.
- `ticket-writing`: writes Epics, user stories and investigation Tasks in Markdown with Gherkin
  acceptance criteria, starting from the spec when there is one. Platform-agnostic.
- `retro-spec`: reverse-engineers a living spec from an existing codebase, with every inference
  flagged.
- `proto-bar`: drops an identical control bar (states, settings, reset) into every HTML prototype.

## Agents

- `analyst`: read-only analysis of one feature for `retro-spec`, run in parallel with your agreement.
  It has Bash (git history, build files), so read-only is enforced by its instructions, not by its
  tool list.
- `reviewer`: adversarial read-only review of a ticket, spec, glossary or skill file against its
  template.

## Hooks

Two `SessionStart` hooks (POSIX `sh`, sharing `hooks/lib.sh`; `jq` used if present, not required):

- `living-specs.sh`: on a project in the format, injects the rules for keeping the specs up to date
  (update without asking, statuses, the `Specs: …` end line, nothing written during a grill-me,
  branch before committing). On a project with an out-of-format `docs/specs/`, or an application
  with no specs, injects a one-line hint to offer the format once. Silent otherwise.
- `glossary.sh`: injects every `docs/glossary*.md` file and the rules for maintaining it, and warns
  above 150 terms. On an application project with no glossary yet, Claude offers once to start one
  (start, not now, never) and creates nothing without your agreement. Silent elsewhere.

The glossary comes from the repository, so anyone with write access to it writes into Claude's
context. The hook frames it as project data that cannot override you, and any instruction inside it
is to be ignored. Above 60,000 bytes (`LIVING_SPECS_GLOSSARY_MAX_BYTES`), it lists the files for
on-demand reading instead of injecting them. A glossary file that is a symbolic link, or that
resolves outside the repository, is never read: Claude only says it was skipped. Review a
third-party glossary before opening a session on the repository, as you would its `CLAUDE.md`.

A project "looks like an application" when its root has a build or dependency manifest
(`package.json`, `pom.xml`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.) or an `index.html`.

## Opting out

Add one of these lines to `CLAUDE.local.md` (kept out of git), `CLAUDE.md` or `.claude/CLAUDE.md`:

- `living-specs: declined`: no spec writing and no format offer for this project.
- `glossary: declined`: no glossary for this project. Answering "never" to the glossary offer
  writes it to `CLAUDE.local.md`.

To stop the offers everywhere, set `LIVING_SPECS_OFFERS=0` (shell profile or the `env` block of
`settings.json`): the hooks then act only on projects that already keep living specs or a
glossary. To keep the plugin out of most projects, install it at project scope instead
(`claude plugin install living-specs@mattdaco --scope project`), only where you want living specs.

When specs move to another repository, `docs/specs/README.md` keeps only `moved_to: <repo or URL>`
and nothing is written there any more.

## Works with code-audits

Optional. If the `code-audits` plugin is installed:

- `code-audits:dev-server` and its Chrome DevTools MCP serve and capture the prototype for
  `screen-spec` and `ticket-writing`;
- `code-audits:security-audit` checks the code against the controls promised in the "Abuse and
  limits" sections, and `code-audits:gdpr-audit` covers the logs they imply;
- `code-audits:legacy-takeover` writes its debt work items in `docs/tickets/`.

Without it, these steps are skipped or done with any static server and browser tooling you have.
If the `dev-workflow` plugin is installed, `retro-spec` keeps its resume point in `HANDOVER.md`.

## Credits

`grill-me` is based on the grill-me skill from
[mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock (MIT). The abuse grid in
`functional-spec/abuse.md` is adapted from
[geoffreycrofte/saas-launch-skillset](https://github.com/geoffreycrofte/saas-launch-skillset) by
Geoffrey Crofte (CC BY 4.0). See `THIRD_PARTY_NOTICES.md` at the repository root.
