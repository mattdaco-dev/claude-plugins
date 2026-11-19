---
name: ticket-writing
description: Use when the user wants to write, improve or challenge a ticket, a user story, an epic, an investigation task or spike, or acceptance criteria, whatever the target platform (Jira, Linear, Notion…), or says "ticket", "write a user story", "write a ticket", "user story", "acceptance criteria", "epic", "a task", "spike", "split into tickets", "rédige une US", "écris un ticket", "critères d'acceptation", "découpe en tickets". Writes Epics, user stories and Tasks in Markdown in docs/tickets/, separating the need, the functional rules and Gherkin acceptance criteria. On a living-specs project, starts from the docs/specs/ sheets (BR-xx, UF-xx, SC-xx, MSG, CALC, Q-xxx) and their screenshots. Platform-agnostic, no access to any ticket tool; reading and publishing are out of scope.
---

# Ticket writing

Goal: turn a need, or a spec, into a **written ticket** with no functional ambiguity, in Markdown,
whatever the platform where it will be created. The skill accesses no platform: it writes the
draft, the user reviews it, and publishing happens outside this skill.

## 0. Scope

**In the skill**: Epic, User Story (US), Task. The Task is an **investigation** (what used to be
called a spike): it is judged on its answer. Written in Markdown, in `docs/tickets/`, in the
language the user works in. The block names below and the Gherkin keywords are given in English:
when the tickets are written in another language, translate them, and use the same names across the
whole folder.

**Out of the skill**:
- **Any ticket platform** (Jira, Linear, Notion…), for reading as well as writing, MCP included,
  even when connected. To rework an existing ticket, the user pastes its content. Reading,
  conversion to a platform's format and ticket creation belong to another skill or tool.
- **Test cases**: they are written separately, on the acceptance test data, by the team that runs
  the acceptance tests.
- Bug and technical development task: **no template** for now. If the code-audits plugin is
  installed, `code-audits:legacy-takeover` has its own template for a debt work item.
- **Management fields** (priority, estimate, sprint, version, assignee, labels): they stay in the
  hands of the BAs and POs.

## 1. Locate the project

The first line that applies decides:

| Situation | Next |
|---|---|
| `docs/specs/README.md` with `moved_to:` | the specs live in the repository indicated: work there in **linked** mode, tickets included (`docs/tickets/` of that repository). Ask for the local path only if the value does not let you find it |
| `docs/specs/README.md` with `format: living-specs` | **linked** mode (section 3) |
| everything else | **standalone** mode: rules and questions carried by the ticket itself |

In standalone mode, do not offer the migration to living specs from this skill: the
`functional-spec` skill and the plugin's SessionStart hook take care of it.

**Location**: `docs/tickets/` at the repository root, created with the first ticket. An older
`tickets/` folder at the root: offer once to move it (`git mv`). Working folder with no project:
write the ticket in the conversation.

**Branch**: drafts are committed on the branch of the current work, or on `docs/tickets-<slug>`,
together with the spec sheets they changed. On the default branch, offer to create a branch before
the first commit. Never push.

## 2. Before writing: what you need to know

Never invent a business rule, a label or a message to fill a gap. If the information is missing, in
this order:
1. ask the user if it blocks the structure of the ticket;
2. otherwise make it an **open point**: a `Q-xxx` in linked mode (section 3), a local question
   `Q<n>` in Open points and a reference `[? Q<n>]` where it applies in standalone mode.

A ticket that owns up to three open questions is worth more than a ticket that hides three.

**The actor is a role, never a person.** Throughout the ticket, context included, write the
business role ("the booking manager"), never a name, a first name or initials, even when a single
person holds the role today. In scenarios, "the user" is enough when the role is unique.

**Business terms** are those of the glossary (`docs/glossary*.md`: `docs/glossary.md`, plus the
`docs/glossary-<domain>.md` it indexes if split) word for word, never a synonym from its "Not to be
confused with" column. A new term goes into it (`glossary` skill).

Questions to ask if the information is not given, and if the spec does not carry it: **which screen
/ which step of the flow**, **which actors**, **which flows** (creation, change, viewing), **what
happens when the display condition stops being true**.

## 3. Linked mode: start from the spec

The spec is authoritative; the ticket is a **deliverable slice** of it. It copies what it cites,
because it will be read on a platform that has no access to `docs/specs/`.

Read before writing: the format (`format.md` of the `functional-spec` skill,
[`../functional-spec/format.md`](../functional-spec/format.md)), `docs/specs/README.md`, the
feature sheet, `domain-model.md`, the `SC-xx` sheets concerned and `questions.md`.

| Ticket | Comes from |
|---|---|
| Epic: Context, Intent, Scope | the Need of the sheet, nothing more |
| Epic: Exit conditions | proposed to the user and validated by them, otherwise an open point; never invented |
| Epic: Open points | the open `Q-xxx` of the sheet: `Q-004 · <question> (assumption: <assumption>)` |
| US: Context, Need | the Need of the sheet and the `UF-xx` the US delivers, fully or partly |
| Functional rules | the `BR-xx` that apply, copied word for word: `BR-04 · <statement>` |
| Acceptance criteria | the steps and decisions of the `UF-xx`, the permissions, the five states of the `SC-xx`, the `CALC-xx`, the lifecycle transitions of `domain-model.md`, the controlled abuses of the Abuse and limits section (one blocked-case scenario per control) |
| Labels in the criteria | `MSG-xx` and `MSG-Uxx` word for word, identifier cited: `Then the message "<wording>" (MSG-03) is shown` |
| Cross-cutting requirements | the business non-functional requirements of the sheet that touch the ticket |
| Open points | the open `Q-xxx` that touch the ticket: `Q-004 · <question> (assumption: <assumption>)` |
| Mockups | the screenshots in `docs/specs/screens/screenshots/`, the Figma links of the `SC-xx` sheet if any, its prototype gaps (section 8) |

**Statuses.** A Proposed `BR-xx`, `CALC-xx`, `MSG-xx`, `MSG-Uxx` or permission is cited with its
status (`BR-04 (proposed) · …`) and adds an open point "BR-04 (proposed) · statement to validate".
An Obsolete element is never cited.

**A gap in the spec is filled in the spec**, according to `functional-spec` section 4 and
`format.md` section 4:
- a rule, a message or a calculation whose statement the user dictated or accepted enters its sheet
  as Validated; a decision they settled but whose statement I write enters as Proposed, statement
  shown for them to accept;
- a rule mentioned without being settled, a gap I spot, or a recommendation of mine, becomes a
  `Q-xxx` in `questions.md` with its assumption, cited in Open points; never a Proposed rule.

The ticket then cites what was added. Never a rule that exists only in the ticket.

**No sheet.** An Epic or a US whose feature has no sheet: offer to formalize it first
(`functional-spec`). If the user refuses, **the whole batch** (the Epic and its US) goes to
standalone mode, and the ticket says so in its Context.

**Several features.** A US that touches several lists them all in `features:`, the main one first.
In the body, a rule from another sheet carries its slug: `BR-12 (fee-management) · …`.

**Moving spec.** When a linked ticket is reworked or delivered, compare each cited statement with its
sheet. A difference (statement rewritten, element turned Obsolete, question answered): update the
ticket, report it, and send a `ready` ticket back to draft.

The end-of-answer "Specs: …" line follows `functional-spec` section 4.

### Split a sheet into tickets

- One Epic per sheet, or per part of a sheet if the user wants it smaller (the Scope says so).
- A US delivers a `UF-xx`, or a part of a `UF-xx` that can be accepted on its own (one actor, one
  flow, one observable behavior). A `UF-xx` that is too big is split by decision branch or by
  actor.
- A `Q-xxx` that needs an investigation becomes a Task.
- **Coverage**: at the end of the batch, each Validated or Proposed `BR-xx` of the sheet is cited
  by at least one ticket, or declared out of the batch in the Epic's Scope. Present the
  `BR-xx → ticket` table to the user.

## 4. Files and frontmatter

One file per ticket in `docs/tickets/`:

| Type | File | Identifier |
|---|---|---|
| Epic | `EPIC-<xx>-<slug>.md` | `EPIC-xx` |
| US | `US-<xxx>-<slug>.md` | `US-xxx` |
| Task | `TA-<xxx>-<slug>.md` | `TA-xxx` |

If the code-audits plugin is installed, the folder also holds the debt work items written by
`code-audits:legacy-takeover`, which follow their own template.

**Elements local to the ticket**: rules `R1`, questions `Q1` (standalone mode) and scenarios
`Scenario 1` are numbered within the ticket and cited there in short form. Cited from outside
(another ticket, acceptance tests, review), they always carry the ticket identifier: `US-003/R1`,
`US-003/Q1`, `US-003/S1`. With no hyphen and no zero-padded digits, they are not confused with the
`BR-xx` and `Q-xxx` of the spec.

Numbering specific to the folder, per type: next number = highest existing + 1. These identifiers
are **local**: the platform assigns its own key when publishing. Slugs lowercase with hyphens, in
the language of the tickets.

Common frontmatter:

```yaml
---
type: us                       # epic | us | task
id: US-003
title: Cancel a started booking
epic: EPIC-01                  # US and Task attached to one; empty otherwise
status: draft                  # draft | ready
updated: YYYY-MM-DD
# linked mode only:
features: [booking]            # slugs of the docs/specs/features/ sheets, the main one first
flows: [UF-02]
rules: [BR-04, BR-07]
screens: [SC-03]
questions: [Q-004]
---
```

- `title`: an infinitive phrase or a noun phrase, no "As a".
- `status: ready` per section 11. Any change to a ready ticket sends it back to draft.
- No platform key or link: they are only known at publishing time, outside this skill.
- The body of the ticket does not depend on the frontmatter: everything a reader needs to know is in
  the body.

**Index**: `docs/tickets/README.md`, created with the first ticket, a table
`| Ticket | Type | Title | Epic | Status |` kept up to date at each ticket created or whose status
changes.

## 5. User Story template

Eight blocks, in this order; "Cross-cutting requirements" and "Mockups" are optional. An optional
block is present or absent, never empty, and the "(optional)" mention is not copied.

```markdown
**Context**
Where we are in the product, which flow, what exists today and why it is not enough.
2 to 4 lines. Someone discovering the product must be able to place the ticket.

**Need**
As <a single actor>, I want <capability>, so that <purpose delivered by THIS ticket>.

**Scope**
In the ticket: ...
Out of the ticket: ... (downstream dependencies, flows deliberately excluded)

**Functional rules**
- BR-04 · <statement copied from the spec>     (linked mode)
- R1. <invariant, declarative sentence>         (standalone mode)

**Cross-cutting requirements** (optional)
- <non-functional requirement checkable in acceptance testing, see below>

**Acceptance criteria**
<Gherkin scenarios, see section 7>

**Mockups** (optional, front-end US)
| Image | Figma | What it shows |
|---|---|---|
| [SC-03-nominal.png](../specs/screens/screenshots/SC-03-nominal.png) | | <state> |
| [US-003_<what-the-frame-shows>.png](screenshots/US-003_<what-the-frame-shows>.png) | [<frame name>](<URL with node-id>) | <state> |
Data shown is fictitious.
Prototype gaps: <those of the SC-xx sheet that touch the ticket>.

**Open points**
- Q-004 · <question> (assumption: <assumption>)  (linked mode)
- Q1. <open question, phrased as a question>     (standalone mode)
- None: write it.
```

Image paths are relative to `docs/tickets/`.

### The "Cross-cutting requirements" block

It carries what acceptance testing checks on every screen and that no business rule states: loading,
error and empty states implemented together with the nominal state, accessibility (tabbing, focus,
`Escape`), and **any departure from the design system validated by the UX team and referenced**. In
linked mode, the business non-functional requirements of the sheet are added, and the states come
from the `SC-xx` sheet: the criteria cover them, don't repeat them here. Keep only what applies to
the ticket.

Do **not** put in it:
- the **test strategy** (component tests, unit tests): the development team adds it;
- the **wording review**: it is done in the mockups or the screen spec.

## 6. The five mistakes to fix every time

Hunt them down in every ticket, including when reworking a ticket provided by the user.

1. **Functional content hidden in the test cases.** The screen, the step, the behavior of an edge
   case are often described there, and nowhere else. Before removing a test case section, extract
   everything that is a rule or a criterion and move it up (into the spec in linked mode).
2. **Several actors, only one declared.** The "As a" names one actor, then a criterion talks about
   another. A single actor in the need; the others are covered by an explicit rule and a dedicated
   scenario.
3. **Several flows, only one covered.** Creation and change are two flows. If the rule applies to
   both, write it; otherwise say which one is excluded. A bug reported on a ticket almost always
   reveals a flow that had no criterion.
4. **A "so that" the ticket does not deliver.** If the purpose depends on another system, it goes in
   Context or in Out of the ticket. The "so that" must be checkable when accepting the ticket.
5. **A behavior described negatively.** "The field must not be filled in" does not say whether it is
   hidden, disabled or optional. Rephrase positively, or make it an open point.

## 7. Acceptance criteria

- **Rule or scenario?** An invariant that holds everywhere is a **rule**. Putting it in Gherkin
  multiplies the scenarios by combination. What is **observable and testable in a given flow** is a
  **scenario**.
- A scenario has **a name** and **a single behavior**.
- Complete structure: `Given` (context) / `When` (action) / `Then` (observable result). Never a
  cascade of `Then` with no context.
- Visible labels (error message, button caption) are part of the criterion, in quotes, word for
  word. A variable part becomes a parameter between angle brackets: "This addition will take the
  room from <current capacity> to <capacity after the addition> seats".
- Cover: the nominal case, the blocked case, each actor that behaves differently, each flow, and
  the edge case where the display condition stops being true.
- **The blocked abuse case.** Each abuse control of the ticket (cap reached, object outside the
  actor's scope, action repeated too fast) has its scenario, with the message shown word for word:
  "Given a user who has reached today's export limit, When they start an export, Then the export is
  refused and the message "…" (MSG-07) is shown". The control is checked server-side: the scenario
  does not stop at a greyed-out button. In linked mode, these controls come from the Abuse and limits
  section of the sheet; in standalone mode, a feature that writes, exports, sends or is open to the
  public without any known limit adds the open point "how could it be misused, and what prevents
  it?" (grid: [`../functional-spec/abuse.md`](../functional-spec/abuse.md)). In linked mode, each
  cited `BR-xx` has at least one scenario that puts it to the test, or the mention of the ticket
  that covers it (`covered by US-005`).
- **Number and name** each scenario: `Scenario 1: <what it demonstrates>`. The number is used to
  cite it in acceptance testing and review. An inserted scenario renumbers the following ones.
- **No test data in a criterion**: no room, customer or booking name or number, no amount, no date,
  no item reference. Describe the condition in generic terms ("an unavailable item", "a date after
  today").
- **Exception, calculations**: a criterion that checks a calculation reuses the fictitious values of
  the `CALC-xx` example (linked mode) or of the calculation rule (standalone mode), citing the
  calculation. Several sets of values: a `Scenario Outline` with its `Examples`.
- In standalone mode, a rule taken from a detailed technical design (one block per endpoint, rules
  numbered `R1`, `R2`… in each block) is copied as a rule of the ticket, with its own number `R<n>`,
  and its origin at the end of the line: `R3. <statement> (design: POST /bookings, R2)`. The block's
  `R2` is never reused as the ticket's number: cited alone, `US-003/R3` always means the ticket's
  rule.

Standard block:

```gherkin
Scenario 1: <what the scenario demonstrates>
  Given <initial state>
  And <condition>
  When <actor's action>
  Then <observable result>
  And <checkable side effect>
```

## 8. Mockups

Never an invented link or image. With no source, the block stays absent.

**Linked mode**: the screenshots already exist, taken by `screen-spec` (one per state, 1440 px).
List them from `docs/specs/screens/screenshots/`, only those of the states the criteria describe.
Nominal, loading or error screenshot missing, or `screenshots_taken` of the sheet older than its
`updated`: offer to retake them with `screen-spec` section 4 before delivering, without capturing
yourself. The empty and no-access states have a screenshot only if the proto can show them. Copy
under the table the "Prototype gaps" of the sheet that touch the ticket: a screenshot shows the
proto, not the target.

**Standalone mode, running prototype**: capture with the Chrome DevTools MCP (serve the proto with
`code-audits:dev-server` if the code-audits plugin is installed, otherwise any static server),
window 1440 × 900, one screenshot per entry point and per state of the criteria, no more. If the
proto has the `proto-bar` bar, follow `screen-spec` section 4 to pick the state and hide the bar.
Save as PNG in `docs/tickets/screenshots/<ID>_<what-the-screenshot-shows>.png`. Remove what belongs
to the review (badges, annotations) and say so when it is not possible. Look at each screenshot
before listing it.

**Figma, in both modes**: only the frames whose URL with `node-id` the user gives, those cited by an
`SC-xx` sheet, or those drawn in the session. Never browse a Figma file; a URL without `node-id`:
ask for the frames wanted. If a Figma MCP is connected, for each frame kept:
- export it with the Figma MCP's `get_screenshot` (`fileKey` and `nodeId` taken from the URL,
  `maxDimension` at 1440), then download the image with the `curl` command the tool provides;
- save it in `docs/tickets/screenshots/<ID>_<what-the-frame-shows>.png`;
- look at it: a working frame (annotations, stacked variants) is not sent as is;
- list it **with the link to the frame**: the link stays the up-to-date source, the image freezes
  what was validated for the story.

Without a Figma MCP, list only the frame links.

Images go as attachments when publishing.

## 9. Epic template

Deliberately light. **Don't list the US**: the real list lives in the attached tickets, and a list
in the description diverges from the first split.

```markdown
**Context**
The problem or the opportunity, at the batch level. 3 to 5 lines.

**Intent**
What the product will be able to do at the end of the epic, phrased from the user's point of view.

**Scope**
In the epic: the main functional blocks.
Out of the epic: what will be handled elsewhere or later.

**Exit conditions**
How we know the epic is done. Not acceptance criteria, closing conditions.

**Open points**
- Q-004 · <question> (assumption: <assumption>)  (linked mode)
- Q1. <open decision at the batch level, phrased as a question> (standalone mode)
- None: write it.
```

## 10. Task template

An investigation is judged on its answer, not on its deliverable. The title says so
("Investigate…", "Compare…").

```markdown
**Question to settle**
A single question, closed if possible.

**Why now**
What is blocked as long as the answer is not known.

**Timebox**
<duration>. Beyond that, stop and report what you have.

**Expected deliverable**
The form of the answer: summary note, throwaway proof of concept, comparison, argued recommendation.

**Stop criteria**
What lets us say the question is settled.
```

In linked mode, a Task often comes from a `Q-xxx`: cite it in Question to settle and in the
frontmatter. The answer, once known, is recorded in `questions.md` according to `functional-spec`
section 4 (status answered, update of what it unblocks).

## 11. Deliver

1. For a batch, write the Epic first, then the US and Tasks attached to it.
2. Write the file or files in `docs/tickets/`, update the index.
3. Run the check (section 12).
4. Show the ticket to the user in the conversation, as rendered Markdown, and ask them to review
   it. Offer a review by the `reviewer` agent, without launching it.
5. **Ready**: with the user's agreement, and only if the ticket has **no open point left**. In
   linked mode: all the `BR-xx`, `CALC-xx`, `MSG-xx`, `MSG-Uxx` and permissions cited are Validated
   and no open `Q-xxx` touches it. In standalone mode: no question `Q<n>` or `[?]` left.
   Otherwise the ticket stays a draft, and say so.
6. Commit the tickets with the spec sheets they changed (section 1, Branch).

Markdown is the output. Conversion to a platform's format and ticket creation are not done here.

## 12. Check

Before showing a ticket, or on request:

- template blocks present and in order, no empty optional block;
- the five mistakes (section 6) hunted down; no test data outside calculation examples;
- each `BR`, `CALC`, `MSG`, `MSG-U` and `Q` cited exists, is not Obsolete, and its statement is
  identical to the sheet's; its Proposed status is shown;
- each cited `BR` has a scenario or the ticket that covers it;
- frontmatter aligned with the body (rules, screens, questions cited); index up to date;
- each image cited exists;
- each `[? Q<n>]` has its row in Open points, and the other way round;
- business terms consistent with the glossary (`docs/glossary*.md`); roles, no person.

## 13. Guardrails

- **No access to a ticket platform**, neither reading nor writing, and no token handled.
- **Never invent** a business rule, a label or an error message.
- **Never a rule that exists only in the ticket** in linked mode: the spec first.
- **Always have the ticket reviewed** before marking it ready.
- Don't produce a test case section.
- When the user provides an existing ticket to rework, **say what was missing**, not only the
  corrected version.
