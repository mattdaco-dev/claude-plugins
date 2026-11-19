---
name: screen-spec
description: Writes and maintains a project's screen specs in docs/specs/screens/ in the living-specs format (one SC-xx sheet per screen with purpose, access, data and formats, actions, display rules, five states, interface messages MSG-Uxx, navigation, dialogs, prototype gaps), with one screenshot of the HTML prototype per state. Describes the target screen of the real application and feeds the tickets. Use whenever an HTML prototype is built or changed in a living-specs project, or when the user says "screen spec", "screen sheet", "UX spec", "document this screen", "retake the prototype screenshots", "spec d'écran", "fiche écran", "refais les captures du proto".
---

# Screen spec

One sheet per screen: what it shows, what can be done there, how it behaves in all its states. It
goes with the mockups in the tickets and serves the development of the real application. It
describes **the target**, not the prototype: what the proto simulates goes into "Prototype gaps".

Shared format: [`../functional-spec/format.md`](../functional-spec/format.md). Read it before any
writing (it also says which parts stay as defined and which are written in the user's language).
Template: [`screen-template.md`](screen-template.md).

## 1. Prerequisite

Locate the project as in `functional-spec` section 1 (decline, move, marker):

- project in living specs: go on;
- `docs/specs/` missing: create nothing on your own, offer the migration (`functional-spec`
  section 5). On explicit invocation of this skill, follow the "nothing" lines of `functional-spec`
  section 1; when they lead to initialization, do only step 1 of `functional-spec` section 2
  (README, domain model, questions, glossary), without chaining into its section 3, then write the
  screen sheet, even if the functional spec is still to be written;
- `docs/specs/` out of format: write no sheet there. Offer the migration (`functional-spec`
  section 5); on explicit invocation, ask whether to migrate first: yes, migrate then write the
  sheet; no, write no sheet;
- declined, or specs moved elsewhere: write nothing unless explicitly asked.

## 2. One screen, one identifier

- New screen: next `SC-xx` (global numbering, `format.md` section 3), sheet
  `docs/specs/screens/SC-xx-<slug>.md` copied from the template, row added to the Screens table of
  the README.
- **The same identifier in the proto**: id of the screen's container or route (`#SC-03`), so that
  sheet, proto and screenshots match without a mapping table.
- A dialog box has no `SC` of its own: Dialogs section of its screen, identifier `SC-xx-<name>` at
  the start of its heading (`### SC-03-cancellation …`), which serves as its anchor (`format.md`
  section 3).

## 3. Fill in the sheet

At creation, then at each change that shows in the sheet (data, label, action, state, navigation,
display rule, message); a styling tweak does not count:

- **Purpose, access**: roles and scope, entry point, what happens without the permission.
- **Labels**: the glossary terms (`docs/glossary*.md`) word for word; a new business term that
  appears on screen goes into it (`glossary` skill), the glossary being created if missing.
- **Content**: areas, then each data item with its exact label, its format and the `BR-xx` it
  depends on. If the project has formatting conventions (design system, installed data formatting
  skill, team guide), they apply: note only what is specific to the product. Otherwise, set the
  format of each data item in the sheet (for example a date `DD/MM/YYYY`, an amount with two
  decimals and its currency), and the same format everywhere.
- **Actions**: availability condition stated positively, effect, next screen, rule and message.
  Each AI track kept in the feature sheet (AI assistance section) that concerns the screen becomes
  an action there ("Suggest a reply", "Translate"…): where it is triggered, what the user reviews
  or edits before the result applies, how they discard it, and its loading and error states
  (manual fallback). A kept track with no visible action says so.
- **Display rules**: each one cites its `BR-xx` (link to the sheet that defines it). A rule that
  does not exist yet is added to the functional spec (`functional-spec` section 4), not only
  described here.
- **States**: nominal, empty, loading, error, no access. A state that does not apply says so in one
  line. The three states of the `proto-bar` bar (nominal, loading, error) are visible in the proto;
  empty and no access are described even if the proto does not show them.
- **Interface messages** `MSG-Uxx` word for word, next number at project level (`format.md`
  section 3), with Status and Source like the `MSG-xx` (`format.md` section 4): Validated if the
  user dictated or accepted the wording, Proposed otherwise; a wording mentioned without being
  settled goes into a question. The `MSG-xx` of the feature sheets are cited, not rewritten.
- **Prototype gaps**: hard-coded data, no server, state forced by the bar, demo shortcut,
  simplified behavior.
- `updated` set to today's date; a `validated` sheet goes back to `in review`; frontmatter
  `screens:` of the feature concerned kept up to date, and the README aligned.

The end-of-answer "Specs: …" line follows `functional-spec` section 4.

## 4. Screenshots

Retaken **on request**, or offered when wrapping up work on the proto (commit, handover, the user
announcing the end), not at every change. One screenshot per state visible in the proto, 1440 px
wide. The procedure below assumes the `proto-bar` bar and `#SC-xx` routes; without them, see
"Without proto-bar or route" further down.

1. Serve the proto (with `code-audits:dev-server` if the code-audits plugin is installed, otherwise
   any static server already running or one you start) and open it with the Chrome DevTools MCP
   (shipped by the code-audits plugin, or configured separately); `emulate` the viewport
   `1440x900x1`.
2. For each screen and each state:
   - navigate to the screen (`#SC-xx`);
   - pick the state by clicking its button in the bar's state selector (not in a proto-specific
     setting that would have the same value):
     `document.querySelector('.pb-seg[aria-labelledby="pb-l-__state"] [data-value="loading"]').click()`.
     Button to file mapping: `ok` → `nominal`, `loading` → `loading`, `error` → `error`;
   - hide the bar during the capture:
     `document.querySelector('.pb').style.display = 'none';`
     `document.documentElement.style.setProperty('--proto-bar-h', '0px');`;
   - `take_screenshot` to `docs/specs/screens/screenshots/SC-xx-<state>.png`, full page if the
     screen overflows. `empty` and `no-access` only if the proto can show these states (setting,
     data);
   - show the bar again (`style.display = ''`, `removeProperty('--proto-bar-h')`).
3. Proto-specific settings (profile, variant): capture the default value. Another value is captured
   only if it changes the screen enough to deserve its own screenshot, named
   `SC-xx-<state>-<value>.png`.
4. Update `screenshots_taken` in the frontmatter, the Screenshot column of the sheet's States table,
   the image under the heading (nominal screenshot) and the Screenshot column of the README.

**Without proto-bar or route.** Proto without the bar, without `#SC-xx` routes, or existing
application (sheet from `retro-spec`):

- reach the screen through the interface (clicks from the home page, application URL) and the
  state through what the proto or the application allows (data, setting, network cut with
  `emulate` for an error);
- a screen or a state you cannot reach: ask the user how to get there, or to provide the
  screenshot; failing that, "no screenshot" in the Screenshot column of States;
- for a proto, offer to add the bar (`proto-bar` skill) and the `SC-xx` identifiers, which make the
  next screenshots reproducible.

Screenshots are committed with the sheet. No Figma export here: a Figma mockup given by the user is
cited by its link in the sheet, without exploring the file.

## 5. Check

- each screen of the proto has its sheet and its row in the README, and the other way round;
- same labels in the sheet and in the proto, consistent with the glossary;
- the five states are covered; each screenshot cited exists;
- each `MSG-Uxx` is defined only once across `docs/specs/screens/`, no number reused
  (`grep -rhoE 'MSG-U[0-9]+' docs/specs/screens | sort | uniq -c`, read together with the
  citations), and has a status and a source;
- each `BR-xx`, `MSG-xx` or `Q-xxx` cited exists.
