---
status: draft
updated: YYYY-MM-DD
screens: [SC-01]
---

# Feature name

## Need

- **Goal**: what the feature makes possible, and why.
- **Actors**: roles involved (see the README).
- **Scope**: what is included; **out of scope**: what is not, explicitly.

## User flows

### UF-01 Flow name

- **Trigger**: who does what, or which event.
1. Role: action.
2. System: processing (BR-01).
3. Decision "short question?"
   - yes: continue → step 4;
   - no: refusal, message MSG-01, end.
4. …
- **Result**: final state, message shown.

## Business rules

| Rule | Statement | Status | Source | Screens |
|---|---|---|---|---|
| BR-01 | One declarative sentence, testable on its own. | Validated | grill-me YYYY-MM-DD | [SC-01](../screens/SC-01-slug.md) |
| BR-02 | ~~Dropped statement.~~ | Obsolete | grill-me YYYY-MM-DD; dropped YYYY-MM-DD: reason | |

## Calculations

Recommended if the feature calculates something, otherwise "not applicable" in one line. An
obsolete calculation keeps its section: heading struck through, status Obsolete, reason and date in
Source.

### CALC-01 Calculation name

- **Status**: Proposed. **Source**: …
- **Inputs**: …
- **Formula**: …
- **Rounding**: …
- **Example** (fictitious data): …

## Messages

Recommended: messages, emails, notifications that the business defines.

| Message | Trigger | Recipient | Wording, word for word | Status | Source |
|---|---|---|---|---|---|
| MSG-01 | when | Role | "Text with <variable>" | Proposed | … |

## Roles and permissions

| Action | Role A | Role B | Status | Source |
|---|---|---|---|---|
| action | yes | own files only | Proposed | … |

## AI assistance

Mandatory: what AI can do for the actors of this feature (suggest, proofread, correct, translate,
summarize, extract, classify, prefill…), track by track, kept or dropped. The behavior of a kept
track and its guardrails are rules `BR-xx` above.

| Track | For whom, at what moment | Decision | Human validation | Data sent to the model | If the AI fails | Status | Source |
|---|---|---|---|---|---|---|---|
| Suggest a reply | Role, when writing a MSG-xx | kept: BR-xx | reviewed and sent by the role | case content, without attachments | manual input, MSG-xx | Proposed | grill-me YYYY-MM-DD |
| Translate | … | dropped: reason | | | | Validated | … |

## Abuse and limits

Mandatory: how a user, a script or a compromised account would misuse this feature, and what that
misuse costs when repeated a thousand times (grid: `abuse.md` of the `functional-spec` skill). A
control kept is a rule `BR-xx` above, with the `MSG-xx` shown when the limit is reached. No abuse
surface: one row that says so, with the reason.

| Abuse | By whom | Cost at scale | Decision | Status | Source |
|---|---|---|---|---|---|
| Export the whole portfolio | Compromised account | Customer data leak | controlled: BR-xx, MSG-xx | Proposed | grill-me YYYY-MM-DD |
| Remind the same customer in a loop | Hurried user | Complaint, image | accepted: reason | Validated | … |

## Business non-functional requirements

Recommended: response times, volumes, retention, availability, expressed by the business and
measurable. Otherwise "not applicable".

## Questions and assumptions

- [Q-001](../questions.md): summary of the question.
- None: write it.
