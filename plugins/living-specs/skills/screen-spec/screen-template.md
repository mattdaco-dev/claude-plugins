---
id: SC-01
status: draft
updated: YYYY-MM-DD
features: [slug]
prototype: path/index.html#SC-01
screenshots_taken: YYYY-MM-DD (proto vN)
---

# SC-01 Screen name

Describes the **target** screen of the application (the existing screen if the sheet comes from
`retro-spec`). What the prototype simulates or simplifies is listed in "Prototype gaps".

![SC-01 nominal](screenshots/SC-01-nominal.png)

## Purpose

What the user comes to do on this screen, in one or two sentences.

## Access

- **Roles**: who can access it, with which scope.
- **Entry**: where it is reached from (menu, link from [SC-xx](SC-xx-slug.md), direct URL).
- **Without the permission**: what happens ("no access" state, redirect, MSG-U03).

## Content

Areas from top to bottom, then the data displayed or entered.

| Area | Role |
|---|---|
| Header | … |

| Data | Area | Display or input | Format | Required | Rule |
|---|---|---|---|---|---|
| Exact label | Header | display, text field, list, checkbox… | e.g. date YYYY-MM-DD, amount with two decimals and currency | yes | [BR-xx](../features/slug.md) |

Formats: if the project has formatting conventions (design system, data formatting skill, team
guide), they apply and only what is specific to the product is noted here; otherwise, set the format
of each data item here.

## Actions

| Action | Available when | Effect | Rule, message |
|---|---|---|---|
| Button label | condition, stated positively | what happens, next screen | [BR-xx](../features/slug.md), [MSG-xx](../features/slug.md) |
| Suggest a reply (AI) | message field empty or not | proposes a text in the field, which the user reviews, edits or discards; loading inside the field, on error MSG-U0x and manual input | [BR-xx](../features/slug.md) |

## Display rules

- What is shown, hidden or disabled depending on the data or the role, citing the rule it derives
  from: [BR-xx](../features/slug.md).

## States

| State | What is shown | Screenshot |
|---|---|---|
| Nominal | … | [screenshot](screenshots/SC-01-nominal.png) |
| Empty | … or "not applicable: the list always contains …" | only if the proto shows it |
| Loading | skeletons in place of the content | [screenshot](screenshots/SC-01-loading.png) |
| Error | message that names the cause and offers a way out (MSG-U02) | [screenshot](screenshots/SC-01-error.png) |
| No access | … | only if the proto shows it |

## Interface messages

| Message | When | Wording, word for word | Status | Source |
|---|---|---|---|---|
| MSG-U01 | empty state | "Text" | Proposed | proto vN |

Functional messages `MSG-xx` come from the feature sheets: cite them, don't rewrite them.

## Navigation

- **Comes from**: [SC-xx](SC-xx-slug.md) (action).
- **Leads to**: [SC-xx](SC-xx-slug.md) (action).

## Dialogs

### SC-01-name Dialog title

Opened by …; content; actions and their effect; messages.

## Prototype gaps

- What the proto simulates (hard-coded data, no server, states forced by the bar) or does
  differently from the target.
- None: write it. Sheet from `retro-spec`: not applicable.

## Questions

- [Q-001](../questions.md): summary.
- None: write it.
