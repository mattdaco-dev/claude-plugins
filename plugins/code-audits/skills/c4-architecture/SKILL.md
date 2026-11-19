---
name: c4-architecture
description: "Analyzes the architecture of an existing project from its code and produces a C4 model in Structurizr DSL (docs/architecture/workspace.dsl), level by level (context, containers, components, deployment, journeys), with validation and export to an interactive static site through the structurizr binary (Homebrew or jar, no Docker). Proposes which levels to do together and where to stop depending on the project. Reused by legacy-takeover. Use when the user wants architecture diagrams of a codebase, or says \"C4\", \"C4 diagram\", \"architecture diagram\", \"Structurizr\", \"workspace.dsl\", \"context diagram\", \"container diagram\", \"component diagram\", \"map the architecture\", \"document the architecture\", \"schéma C4\", \"diagramme d'architecture\", \"documente l'archi\"."
---

Goal: a C4 model **true to the code**, at the level of detail that serves the project and no more.
The skill describes what exists; it does not design an architecture (see "Out of scope").

Skill files:
- [`references/dsl.md`](references/dsl.md): useful syntax and checked pitfalls. **Read it before
  writing the DSL.**
- [`examples/workspace.dsl`](examples/workspace.dsl): validated example, one view of each type
  (C1, C2, one C3, journeys, deployment). The split C3 and the `Assumed` tag are shown in
  `references/dsl.md`.
- [`scripts/c4.sh`](scripts/c4.sh) (in this skill's directory; call it by its absolute path):
  `check <workspace.dsl>` (validation then inspection) and
  `export <workspace.dsl> [format] [folder]` (format `static` by default, folder `site/` next to
  the workspace). Exit codes:
  - 0: `VALID` then `INSPECTION OK`, or `EXPORTED`;
  - 1: `INVALID` (invalid DSL, `ERROR` messages follow), `EXPORT FAILED`, or incorrect call
    (missing arguments, workspace not found, unknown format or action);
  - 2: `INSPECTION`, inspector findings follow (the DSL is valid);
  - 3: `structurizr` not on the `PATH`;
  - 4: `TOOL ERROR` (Java, crash): do not touch the DSL, show the message;
  - 5: output folder refused (it contains the workspace, is a git root, `$HOME`, `/`, contains
    tracked files, or is not empty without coming from a previous export).

## 0. Tool

`command -v structurizr`. Missing: offer, without installing it unasked,
- `brew install structurizr` (pulls openjdk, about 900 MB installed);
- or, if Java 21 or later is already installed another way (or without Homebrew): download the
  `.war` of the latest release from https://github.com/structurizr/structurizr/releases and put on
  the `PATH` a `structurizr` script that runs `java -jar <path>/structurizr-<version>.war "$@"`
  (this is what the Homebrew formula does). `c4.sh` only calls the `structurizr` command.

Declined: the skill goes on, the DSL is written but marked **not validated** in the output README,
and no rendering is produced; at each level, the user then validates a table of elements and
relationships instead of the site. No Docker, no online editor (the architecture code does not
leave the machine).

## 1. Framing

- **Repos**: the current repo, or several repos that form one system. In that case, ask for their
  local paths and the **host repo** of the model (the one that receives `docs/architecture/`). A
  container whose code is not provided is modeled, tagged `Assumed`, and the question is asked.
- **Systems**: a workspace models a single system with containers (`scope softwaresystem`). A
  monorepo that holds several independent systems gives one workspace per system, in
  `docs/architecture/<system>/`; ask which one to start with.
- **Existing material**: look for `**/*.dsl`, `**/*.puml`, `**/*.mmd`, `**/*.drawio` outside
  dependencies.
  - A workspace produced by this skill (output README present) is completed from the levels
    validated in it.
  - A workspace outside these conventions (elsewhere, no README, labels in another language,
    `!include`, `workspace extends`, manual layout in `workspace.json`): ask whether to complete it
    as is or to redo it in `docs/architecture/`.
  - PlantUML, Mermaid or draw.io diagrams: discovery sources like the docs, no conversion unasked.
  - An existing element that the code contradicts is reported to the user, never corrected
    unasked.
- **Language**: identifiers in English (`roomBooking.api`), labels in the language the user works
  in (names, descriptions, relationships, view titles). A component keeps the name of its class or
  module. Detail in `references/dsl.md`.
- **Vocabulary**: the names of actors, systems and containers are business terms. Reuse the ones
  from the project glossary (`docs/glossary*.md`) if it exists. If it is missing, the project is
  an application project and the `living-specs` plugin is installed, create it with
  `living-specs:glossary`, terms with the Proposed status; otherwise skip. If the output is outside
  the repo, or the user does not want anything written in it, no glossary is created: the chosen
  terms go into a "Terms" section of the output README.
- **Freshness**: for each repo, date of the last commit and gap with the remote branch
  (`git log -1 --format=%cd`, `git status -sb`). A clone several weeks old or behind: suggest the
  user pulls before discovery (a fetch run by the agent may fail if the SSH key is protected by a
  passphrase). The output README records the branch and commit modeled.
- **Output**: `docs/architecture/` in the host repo, unless another path is given.
- **Branch** `docs/architecture-c4` before the first commit (never commit on the default branch),
  unless already on a working branch.

## 2. Discovery (read-only)

| Source | What it gives |
|---|---|
| README, `docs/`, ADRs, existing diagrams | role of the system, actors, vocabulary |
| manifests (`package.json`, `pom.xml`, `build.gradle`, `go.mod`…), monorepo modules | containers, technologies and versions |
| `Dockerfile`, compose, Helm, k8s, OpenShift, Terraform, deployment pipelines | deployed containers, databases, queues, deployment |
| config (`application*.yml`, `.env.example`, `environment*.ts`) | databases, queues, external systems (host and protocol) |
| HTTP clients, SDKs, message producers and consumers | outgoing relationships and their protocol |
| security (roles, OIDC, SSO) | actors, authentication system |
| routes, controllers, packages, modules | components (C3), journey entry points |
| `docs/specs/` (user flows `UF-xx` in `docs/specs/features/`) if the project uses living specs | journeys |

**Secrets**: config and `.env` files often contain passwords in clear.
- A real `.env` is not displayed: only its variable names, with
  `grep -oE '^[A-Za-z_][A-Za-z0-9_]*=' .env`.
- In config, record only keys, hosts and protocols, never a credential value (`password`,
  `secret`, `token`, `user:pass@` in a URL).
- No URL with a username, token or password in the DSL or the README.

**Proof or tag**: an element or relationship seen only in the docs, a config URL with no client in
the code, an actor deduced from a role with no screen: tag `Assumed` (dashed border, dotted
relationship). An unknown technology is written "to confirm". The output README lists both.

**The code is the reference**: when the docs (README, `CLAUDE.md`, architecture docs) contradict
the code, the model follows the code and the gap goes into the output README, with the file and
line on each side. The docs are not corrected unasked. Gaps are also reported in the project's
context file (`AGENTS.md` if that is the chosen file, otherwise `CLAUDE.md`), which later sessions
read.

**Actors**: a role, never a person. The code rarely shows all the actors: ask the question at the
first level rather than inventing some.

**Size**: physical lines of a container, tracked text files only, excluding tests, generated code
and dependencies, as in the `legacy-takeover` quick mode (§1 point 3):
`git grep -I -c '' -- <directory> ':!<excl>' | awk -F: '{s+=$NF} END {print s+0}'`
(`<excl>`: tests, generated code, vendored code; one exclusion per `':!<pattern>'`). `cloc` will do
if it is already present.

## 3. Levels and groupings

Before writing, announce the plan proposed for this project, with its reason:

| Level | When | Default grouping |
|---|---|---|
| **C1 context** | always | with C2 |
| **C2 containers** | always | with C1; + deployment if the infra is in the repo |
| **Deployment** | infra readable in the repo (Helm, k8s, Terraform, pipeline); otherwise never, it would be guessing | with C2 |
| **C3 components** | a container that deserves it (§5), one at a time | alone |
| **Dynamic views** | a known key journey (provided, from `docs/specs/`, from `living-specs:retro-spec` or from `legacy-takeover` §2.3) | after C2; container scope if its C3 exists |
| **C4 code** | not recommended: a class diagram is stale by the next commit. Only on request, for a specific mechanism | alone, outside Structurizr (the IDE does it better) |

**Exceptions to the C1 + C2 grouping**:
- **C1 alone first** when the context is uncertain: more than five external systems, actors not
  visible in the code, blurry system boundary (monorepo, several repos). Validate the context
  before building on it. When moving to C2, the relationships written between systems are
  replaced by those of the containers (the context deduces them), not duplicated.
- **C1 + C2 + C3 at once** for a very small project: a single application container, less than
  10,000 lines. C3 is then the only view that says something; this case overrides the stop after
  C2 of §5.

**Dynamic view**: system scope by default (`dynamic app`, steps between containers); container
scope (`dynamic app.api`, steps between components) only if that container's C3 exists. Three or
four at most: beyond that, it is a spec, not a diagram.

**Busy C3**: beyond a dozen components or when arrows cross, split into several views of the same
container along a readable axis (business domains on one side, cross-cutting services on the
other), with explicit `include` and `exclude` of relationships already shown elsewhere
(`references/dsl.md`). The model stays single, only the views are split.

## 4. Loop per level

1. Write or complete `workspace.dsl` (skeleton and pitfalls: `references/dsl.md`).
2. `scripts/c4.sh check <workspace.dsl>`:
   - `INVALID` (code 1): fix from the message, run again;
   - `INSPECTION` (code 2): fix the findings (missing description or technology, element without a
     view). Do not silence a finding with an `ignore` property, except documentation and decisions
     (already ignored in the skeleton). What is not known is written "to confirm", nothing is made
     up to satisfy the inspector;
   - **three attempts at most** for each, then show the remaining messages to the user;
   - code 4: tool problem, the DSL is not at fault, show the message.
3. `scripts/c4.sh export <workspace.dsl>`: static site in `site/` next to the workspace, openable
   via `file://` (link given by the script, anchor `#<view-key>`).
4. Present: the views produced and their link, the `Assumed` and "to confirm" elements, the
   questions. Offer to open it in Chrome (chrome-devtools MCP, bundled with this plugin) for a
   screenshot if the user wants to see it in the conversation. After a new export, Chrome keeps the
   old site in cache when only the anchor changes: reload, or add `?v=<n>` before the anchor.
5. The user validates or corrects. Corrections applied, then back to 2.
6. **Recommendation for what comes next** (§5): continue with a given level and why, or stop. The
   user decides. The output README is updated at each validated level.

## 5. Where to stop

The signals are read **container by container**:

- **C3 signals** (count at least two to recommend the C3 of a container):
  - more than 10,000 lines, or clearly larger than the other containers;
  - dense business logic (calculations, rules, orchestration), not only data exposure;
  - hotspot or high risk (returned by `legacy-takeover` or `maintainability-audit`).
- **Eliminating condition**: a readable internal structure (packages or modules by domain).
  Without it, the C3 would only show spaghetti: no C3, and the finding goes into the output README
  ("C3 of the API not done: no internal structure").

Exception: when called by the `legacy-takeover` full mode, high risk alone is enough to do the C3
of an in-scope container, under the same eliminating condition (§8).

Recommend **stopping after C2** when no container gathers two C3 signals (typical case: monolith
or small application, thin CRUD or pass-through containers), except the very small project of §3
and the takeover full-mode exception above. The need counts too: to explain the system
(onboarding, architecture review, operations file), C1 and C2 are almost always enough, and a C3 is
only proposed on request.

Recommend a **dynamic view** when a journey crosses at least three containers or components, or
carries a risk.

## 6. Output

```
docs/architecture/
├── workspace.dsl     # source of truth, versioned
├── README.md         # versioned
└── site/             # export, ignored by git, regenerated by c4.sh export
```

- Ignore `site/`: a `<path>/site/` line in the project's `.gitignore` (or in `.git/info/exclude`
  if the user does not want anything written in the repo).
- `README.md`, short:
  - the command to regenerate and open the site, with real paths:
    `<skill directory>/scripts/c4.sh export <path>/workspace.dsl` (it replaces a previous export
    without risk for the rest of the folder, and gives the `file://` link), tool installed per §0.
    The skill directory belongs to the installed plugin and can move with plugin updates: say so
    in one line;
  - validated levels, with their date, and levels set aside with the reason ("C3 not done: thin
    containers");
  - `Assumed` elements, "to confirm" technologies and open questions;
  - gaps between the docs and the code (§2);
  - branch and commit modeled for each repo;
  - "Terms" if no glossary is written in the repo (§1);
  - "not validated" at the top if `structurizr` did not run.
- Commit: `docs(architecture): add C4 model (<levels>)`, then
  `docs(architecture): add <level> view` for each addition.

## 7. Checks before presenting

- each element has a description; each container and component, a technology with its version
  when known, "to confirm" otherwise;
- each relationship says what happens (a business verb, never "Calls" or "Uses") and over which
  protocol;
- external systems tagged `External`, databases `Database`, front end `Web Browser`;
- what is not proven by the code is `Assumed`;
- no secret value, no URL with credentials;
- names aligned with the glossary;
- `check` returns `VALID` and `INSPECTION OK`, or the README says "not validated" (§0).

## 8. Called from `legacy-takeover`

The takeover gives the mode, the `<docs>` root (which replaces `docs/`), the risk map and, in full
mode, the debt register. The commit follows the takeover's. If the takeover does not write into the
repo, `site/` is ignored through `.git/info/exclude`, or nothing if `<docs>` is outside the repo,
and no glossary is created in the repo: the terms go into the "Terms" section of the README (§1).

The rule below is the only one that sets the risk level of a container; the takeover points to it.

**Risk level of a container** (tag `High risk` or `Medium risk`, low has none):
- quick: the highest level among the risk map modules it hosts. A container with no module from
  the map (database, queue, static front end) has no tag, unless a red flag targets it (database
  without backups, EOL image);
- full: recomputed from the register. High if it carries an exposed High or Critical `TD-xx` row
  (hotspot or critical path), medium if it carries a Medium row or a non-exposed High one. Same
  rule for the components of the C3s.

**Quick**: C1 + C2 in a single pass, without the grouping exceptions of §3 (whatever is uncertain
becomes `Assumed`), a single validation by the user, no recommendation for what comes next (the
takeover goes through its own steps), no install proposal: without `structurizr`, the DSL is marked
not validated. The title of the C2 view says that the borders show the risk.

**Full**:
1. risk tags recomputed;
2. C3 of the in-scope containers now at high risk, under the eliminating condition of §5 (a
   refusal is recorded in the README);
3. one dynamic view per critical path, four at most, starting with the ones that cross a high-risk
   container; the others are listed in the README.

## Out of scope

- Designing a target architecture: `living-specs:grill-me` to challenge the design, then
  `dev-workflow:adr` to record the decisions, if those plugins are installed; otherwise a regular
  design discussion.
