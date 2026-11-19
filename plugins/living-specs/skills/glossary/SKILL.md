---
name: glossary
description: Creates and maintains the business glossary of an application project in docs/glossary.md (term, definition, not to be confused with, source, status Proposed/Validated), injected into the context of every session by the plugin's hook. Mandatory deliverable of retro-spec, functional-spec and screen-spec. Use when a business term is defined, clarified or corrected in a session, when the user says "glossary", "business vocabulary", "add this term", "define this term", "what does X mean", "glossaire", "vocabulaire métier", "ajoute ce terme", or when a project has no glossary yet.
---

# Glossary

The glossary fixes the project's **business vocabulary**: what each term means, and what it must not
be confused with. The plugin's SessionStart hook injects it into the context of every session: a
term defined once no longer needs to be explained again. Without the hook (plugin hooks disabled,
or session opened outside the repository), read the glossary as soon as the session touches the
business domain.

Write entries in the language the user works in. The column names and status values stay as in the
template.

## 1. Where and for which projects

- File: `docs/glossary.md` at the repository root, independent of the specs, or one file per domain
  (section 6). A project in living specs points to it from `docs/specs/README.md`; a project that
  declined the specs still has it.
- **Mandatory** on every application project (app, prototype, feature).
- **Excluded**: tooling or configuration repository (dotfiles, Claude Code config, plugin
  repository), working folder with no application project (notes, documents, one-off exchanges),
  and a project whose `CLAUDE.local.md`, `CLAUDE.md` or `.claude/CLAUDE.md` contains the line
  `glossary: declined`.

## 2. Create

Without asking, at the **first business term** met in the session (no empty file created ahead of
time), if it is missing, that is, if no `docs/glossary*.md` file exists (a split glossary counts,
section 6): copy [`glossary-template.md`](glossary-template.md) to `docs/glossary.md`, replace
`PROJECT_NAME`, replace the example row with the term. Report it in the end-of-answer line
("Glossary: created, 1 term").

`retro-spec`, `functional-spec` (section 2) and `screen-spec` create it if missing, with the terms
they meet.

## 3. What a term is

A word or an expression **specific to the business or the project**, or used with a precise
meaning: business objects, statuses, roles, acronyms, names of operations, labels whose meaning is
not obvious. Not everyday vocabulary nor generic technical vocabulary ("button", "API",
"database"), unless it has a particular meaning here.

## 4. Write an entry

- **Term**: the exact form, the one that will be written everywhere; an acronym with its long form
  ("DN, delivery note").
- **Definition**: what the term means **in this project**, in one or two sentences, without the
  term itself in its definition.
- **Not to be confused with**: synonyms to avoid (always write the term, never the synonym), false
  friends, misleading name ("ClosedCase: archived case, not necessarily processed"), neighbouring
  term to tell apart.
  Empty if nothing.
- **Source**: `discussion YYYY-MM-DD`, `grill-me YYYY-MM-DD`, `code src/x.ts:42`, `doc <file>`.
- **Status**: **Validated** if the definition was dictated by the user, or written, shown and then
  accepted as is; **Proposed** if it is inferred from what exists (code, doc) or written by Claude
  from the user's explanation without having been shown to them. No invented definition: a term
  whose meaning is unknown becomes a question (`Q-xxx` in `docs/specs/questions.md` if the project
  is in living specs, otherwise a question asked to the user) and does not enter the glossary until
  it is defined.
- Alphabetical order.

## 5. Keep it up to date

This part applies **without asking**:

- new term, defined or clarified in the exchange: add the entry;
- corrected definition: a Validated entry is rewritten only with the user's words; a Proposed entry
  is corrected and stays Proposed until accepted;
- renamed term: the old name goes into "Not to be confused with" of the new one; in a project in
  living specs, replace the old name in `docs/specs/`;
- dropped term: delete the entry, unless it remains in the code or the data (say so in the
  definition then);
- during a grill-me, note the terms and write them at the end, with the formalization.

At the end of the answer, one line says what moved ("Glossary: Fee added (proposed)"); no line if
nothing moved. It can be combined with the "Specs: …" line.

Specs, screens, tickets and answers use the glossary terms word for word; a synonym from the "Not to
be confused with" column gets corrected.

## 6. Size and splitting

The hook injects the whole glossary, all files included, and warns when it exceeds 150 terms.
Without the hook, count yourself (table rows) when adding to it. Above 150 terms, offer to prune
(dropped terms, everyday vocabulary) or to split by domain.

Once split, the glossary is held in several `docs/glossary-<domain>.md` files (each copied from the
template, heading "Glossary: PROJECT_NAME, <domain>"), all injected by the hook. `docs/glossary.md`
stays, as the index: the list of files per domain, and the terms shared by several domains. A term
is defined in one file only: the one of its domain, or the index if it is cross-domain; a new term
goes into the file of its domain. The skills that read the glossary (`functional-spec`,
`screen-spec`, `retro-spec`, `ticket-writing`) read every `docs/glossary*.md` file.
