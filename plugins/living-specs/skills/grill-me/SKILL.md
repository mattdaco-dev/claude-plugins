---
name: grill-me
description: Interview the user relentlessly about a plan, design, idea, or chosen solution until reaching shared understanding, resolving each branch of the decision tree. Use when the user explicitly asks to be challenged or interrogated, or says "grill me", "grill", "challenge me", "challenge-moi sur…", "interroge-moi". Also use when, after you proposed several ideas/solutions/analyses, the user asks to pressure-test the option they picked ("challenge this choice", "grill this option", "challenge ce choix"), not merely because they selected an option or asked for more detail.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one: settle a decision before the ones that depend on it, and don't drop a branch you opened. For each question, provide your recommended answer.

Ask the questions **one at a time**, and wait for my answer before asking the next:

- when the question has a few plausible answers, use the `AskUserQuestion` tool, one question per call, with your recommended answer as the first option labelled "(Recommended)";
- when it is open (a name, a figure, a description, a "why"), ask it in plain text with your suggested answer, instead of forcing artificial options.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

Ask in the language the user works in.

## AI track, on every functional need

When a branch is about how the product answers a functional need (a user writes, reads, searches, sorts, fills in, decides, communicates), always ask one question about what AI could do there, with concrete suggestions tied to the need: draft or suggest a reply, proofread and correct, translate, adapt the tone, summarize, extract data from a document, classify or route, prefill a form, detect an anomaly. Recommend the track you find most useful, or recommend dropping it when it brings nothing (the user does it faster alone, a mistake costs too much, the volume is too low). It is a real decision: settle it, don't skip it.

For each track kept, settle its guardrails before closing the branch:

- **human validation**: does a person review the AI output before it takes effect, or does it apply directly;
- **data sent to the model**: which data leaves the application, personal data included (link with the GDPR);
- **failure or slowness**: what the user sees and can still do when the AI fails, times out or returns nothing usable.

A dropped track is kept in the summary with its reason, so the debate isn't reopened later.

## Abuse track, on every functional need

When a branch settles a feature that writes, reads in bulk, sends something, calls a third party
or is open to the public, ask one question about abuse before closing the branch: how would a
user, a script or a compromised account misuse it, and what does it cost when it happens a
thousand times? Load the grid in `../functional-spec/abuse.md` (section 3) and propose the two or
three abuses that fit the feature, with the control you recommend for each. Recommend accepting a
risk when the control costs more than the abuse (low volume, identified and logged internal users).

For each abuse, settle it:

- **controlled**: the control, enforced server-side, and what the user sees when the limit is hit;
- **accepted**: the reason;
- a figure (cap, time window, export size) the user does not settle stays an open question with
  your assumption, not a decision.

A feature with no abuse surface (a user reading their own data, no volume, nothing sent) gets one
line saying so, with the reason. Like the AI track, it is a real decision: settle it, don't skip it.

When every branch is resolved and we've reached shared understanding, stop grilling and summarize the decisions we settled: a concise, actionable plan I can act on. Nothing is written to specs or glossary while grilling; everything happens at the end.

## At the end, on an application project or one of its features

What counts as an application project, and which projects are excluded or have declined, is
defined by the `functional-spec` skill (its section 1 and `format.md` section 2) for specs and by
the `glossary` skill (its section 1) for the glossary: check them there, don't keep a copy here.

- **Project already in living specs** (`docs/specs/README.md` carries `format: living-specs`): formalize the settled decisions without asking, with the `functional-spec` skill (its section 3, written in one block at the end), and end the answer with the "Specs: …" line it requires.
- **Project not in that format**: offer to formalize the decisions with `functional-spec` (offer only, don't chain into it). This offer can carry the format proposal of `functional-spec` section 5.
- **Glossary**: list in the summary the business terms defined or clarified during the grill, then write them to the glossary (`docs/glossary*.md`) with the `glossary` skill (file created if missing, a term is Validated only if I gave or accepted its definition), and end with the "Glossary: …" line.

Based on the grill-me skill from mattpocock/skills by Matt Pocock (MIT). See THIRD_PARTY_NOTICES.md at the repository root.
