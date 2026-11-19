---
name: maintainability-audit
description: "Maintainability audit of a project's code (technical debt): complexity, duplication, dead code, coupling and cycles between modules, test coverage, hotspots (complex files that change often), knowledge concentration. Real tools first (lizard, jscpd, knip, madge, PMD/CPD, radon, vulture…), heuristic fallback otherwise. Produces a dated prioritized report, then proposes only the quick wins, one by one. Use when the user wants a maintainability or tech debt audit, or says \"maintainability audit\", \"tech debt\", \"technical debt\", \"code quality\", \"code smells\", \"hotspots\", \"audit de maintenabilité\", \"dette technique\", \"qualité du code\", \"points chauds\". Reused by the maintenance (maint zone) and legacy-takeover skills."
---

Goal: measure the **maintainability of the code itself** (not the tooling around it, which belongs
to `maintenance`) and say **where the debt really costs**. A complex file nobody touches costs
little; a complex file changed every week, with no test, costs a lot. Usable on its own, or called
by `maintenance` (`maint` zone). Audit first, read-only: no audit command writes into the project
(no build, no `sbt`, no install). **Never run `git push`.**

## 0. Preamble

1. **Stack and scope**: read the manifests (`package.json`, `angular.json`, `tsconfig.json`,
   `pom.xml`, `build.gradle(.kts)`, `build.sbt`, `pyproject.toml`, `requirements.txt`…) and the
   sources. On a large project, the user can restrict to one module: respect that.
2. **Exclusions**: generated code (OpenAPI clients, protobuf, `generated/`), build outputs
   (`target/`, `build/`, `dist/`), vendored code, `node_modules`, database migrations, fixtures,
   lockfiles. Pass them to **every** tool (option given in each command below, `<excl>` = the globs
   in the tool's format: comma-separated for radon, jscpd and vulture, repeated option for lizard,
   `-x "a" -x "b"`) and list them in the report. For `git log`, one exclusion pathspec per glob:
   `':(exclude,glob)**/generated/**' ':(exclude,glob)dist/**' ':(exclude,glob)**/node_modules/**'`,
   written `<git-excl>` below.
3. **Previous run**: the last `maintainability` audit (path per `audit-deliverables` §2) to give
   the **trend**: is the debt going up or down.
4. **Real tools first.** Check presence before running: `command -v <tool>` for binaries,
   `npx --no <tool> --version` for npm packages (without `--no`, `npx` downloads the package).
   Present → run it; missing → **offer** a one-off run or an install outside the project:
   `npx --yes <package>` (npm cache, nothing in the project), `pipx run` or `pipx install`,
   `brew`, global install. **Never install anything in the audited project** (no `npm i -D`, no
   change to the manifest or the lockfile). Declined or failed → heuristic fallback, noted. Called
   through the `auditor` agent: no install and no question possible, direct fallback, tool listed
   as "not run" and the proposal listed under "To do in the main session".

## 1. Hotspots (always, this is the core of the report)

- **Churn** over 12 months (6 months if more than 1000 commits in the year):
  `git log --since=12.months --format= --name-only -- <src> <git-excl> | sed '/^$/d' | sort | uniq -c | sort -rn`.
  A renamed file counts under both names: group the obvious cases by hand.
- **Hotspot** = a file in the top 10 % most changed **and** in the top 10 % largest or most
  complex (§2). Return the top 10 as a table: file, commits, lines, max complexity, tests.
- **Tests** for the file: a matching test file exists (`<name>.spec.ts`, `<Name>Test.java`,
  `<Name>Spec.scala`, `test_<name>.py`) or the coverage report covers it (§6). Otherwise "no".
- **Knowledge concentration**: `git shortlog -sn HEAD -- <file>` (`HEAD` is required: without a
  revision, `git shortlog` reads standard input and returns empty output outside a terminal). For
  each author, `git log -1 --format=%ad --date=short --author=<name>` over the whole repo:
  **departed author** = no commit for 6 months. Report a file with a single author, or whose
  authors have all left.
- Missing or truncated history (zip export, squash): say so, and rank by size × complexity.

## 2. Complexity and size

- **Multi-language**: `lizard -w --CCN 15 --length 100 -x "<excl>" <src>` (Java, Scala, JS/TS,
  Python…), output limited to the functions over the thresholds. This is the default measure.
- **JS/TS**: if ESLint is installed, run it again with the rules on the command line, whether the
  config enables them or not: `npx --no eslint --rule 'complexity: [warn, 15]' --rule 'max-depth: [warn, 4]'
  --rule 'max-lines-per-function: [warn, 100]' <src>` (never create or change a config).
- **Java**: PMD, targeted rules to avoid the noise of the whole category:
  `pmd check -d <src> -f text -R category/java/design.xml/CyclomaticComplexity,category/java/design.xml/CognitiveComplexity,category/java/design.xml/GodClass`.
- **Scala**: read an existing scapegoat report (`target/scala-*/scapegoat-report/scapegoat.xml`).
  Running it goes through `sbt`, which compiles and writes into `target/`: only in the main
  session, with the user's consent. Otherwise lizard.
- **Python**: `radon cc -s -n C -e "<excl>" <src>` and `radon mi -s -e "<excl>" <src>`
  (maintainability index).
- Fallback: longest files and functions, deep nesting, "god" classes (many methods and
  dependencies).

## 3. Duplication

- **Multi-language**: `npx --no jscpd --min-tokens 70 --reporters console --ignore "<excl>" <src>`.
- **JVM**: CPD as an alternative, `pmd cpd --minimum-tokens 100 --language java -d <src>` (or
  `--language scala`).
- Return the **overall rate** and the largest duplicated blocks. Alert threshold: rate > 5 % or a
  block > 50 lines. Duplication between two modules that evolve separately can be intentional:
  report it, do not condemn it.

## 4. Dead code and unused imports

- **JS/TS**: `npx --no knip` (unused files, exports, dependencies; exclusions through `ignore`
  passed as an option or an existing knip config). Unused imports and local variables:
  `npx --no tsc --noEmit --noUnusedLocals --noUnusedParameters -p tsconfig.json`.
- **Python**: `vulture <src> --min-confidence 80 --exclude "<excl>"`.
- **JVM**: no reliable static tool; heuristic (classes never referenced outside tests), to confirm.
- Fallback: `grep` for exported symbols with no usage. Everything found here is **to check before
  deletion** (see §8).

## 5. Coupling and architecture

- **JS/TS**: cycles with `npx --no madge --circular --extensions ts,tsx,js --ts-config tsconfig.json
  --exclude "<regex excl>" <src>` (`--ts-config` resolves `paths` aliases, otherwise some cycles
  slip through), or dependency-cruiser if it is already configured. For Angular, report catch-all
  modules and `shared/` folders that import business code.
- **JVM**: existing ArchUnit tests first (`slices().should().beFreeOfCycles()` makes the rule
  executable): mention them, and their result if the CI publishes it. Otherwise, if compiled
  classes already exist (`target/classes`, `build/classes/java/main`):
  `jdeps -verbose:package <classes>` lists the dependencies between packages; jdeps does not report
  cycles, they have to be **deduced** from that list (A → B and B → A).
- **Python**: `pydeps <pkg> --show-cycles --show-dot --no-output`: a DOT graph of only the modules
  in a cycle on standard output, no file written. Each `a -> b` / `b -> a` pair is a cycle.
  Without `--show-dot`, the output is empty. Empty output with `--show-dot`: no cycle.
- Reading the architecture: bypassed layers (a controller talking to the database), business logic
  in the UI or the mappers, blurry module boundaries.

## 6. Tests and safety net

- **Coverage**: only if a report already exists: `coverage/lcov.info` or
  `coverage/coverage-summary.json` (JS/TS), `target/site/jacoco/jacoco.xml` (Maven) or
  `build/reports/jacoco/test/jacocoTestReport.xml` (Gradle), `target/scala-*/scoverage-report/scoverage.xml`
  (Scala), `coverage.xml` (Python). **Note its date**: older than the last commit on a hotspot, it
  is stale, say so. Otherwise, **estimate** from the structure (ratio of test files to sources,
  modules with no test at all) and **offer** to run the suite with coverage, without doing it
  unasked (through the `auditor` agent: under "To do in the main session"). Alert threshold:
  < 50 % of lines.
- **Hotspots without tests**: cross with §1. This is the finding that weighs the most.
- Apparent quality: tests with no assertion, disabled tests (`skip`, `@Disabled`, `xit`,
  `@pytest.mark.skip`), tests that only do snapshots.

## 7. Declared debt signals

- `TODO`, `FIXME`, `HACK`, `XXX`: count, and the oldest ones (`git blame`).
- Compiler or linter workarounds: `eslint-disable`, `@ts-ignore`, `any` in bulk,
  `@SuppressWarnings`, `# noqa`, `# type: ignore`, `asInstanceOf` in Scala.
- Language or framework versions far behind (EOL details stay in `maintenance`).

## 8. Known false positives

- **Dead code**: dependency injection and decorators (Angular, Spring), routes loaded by string
  (lazy loading), reflection (Jackson, Spring, Akka), Python dynamic imports, entry points declared
  in config. Always check with `grep` before calling something "dead".
- **Complexity**: a long mapping `switch` is low risk; a parser or an algorithm can be complex by
  nature. Judge the risk, not only the number.
- **Duplication**: DTOs, tests and generated code inflate the rate. Exclude them or say so.

## 9. Severity

| Severity | Examples |
|---|---|
| Critical | hotspot with CCN > 30, no test, on a critical path, all authors gone |
| High | hotspot without tests; cycle between business modules; function with CCN > 30 in a hotspot |
| Medium | duplication over the threshold (§3) between active modules; large amount of dead code; coverage < 50 % outside hotspots |
| Low | complexity in stable code; old TODOs; small duplications |

The **critical path** cannot be guessed: ask the user. Through the `auditor` agent, the brief gives
it (`maintenance`, `legacy-takeover`). If it is missing or the brief says it is unknown: rate High
for now, Exposure "hotspot", and list the Critical candidates under "To do in the main session"
("critical paths to confirm"). In a maintenance pass, the orchestrator asks the question when the
collection results come back (`maintenance` §3) and raises to Critical those that touch a confirmed
path; with no answer, they stay High and the summary says so. Shared scale: `audit-deliverables`
§2. Each finding also carries **effort (S/M/L)**, **regression risk**, the **source** (tool or
reading) and its location.

## 10. Output

Deliverables per the **`audit-deliverables`** skill (path, frontmatter, common columns, debt
register), type `maintainability`. Write the report in the language the user works in.

- **Called by `maintenance` or `legacy-takeover`**: return the collection (read-only), no fixes
  here. Heavy refactors are returned as findings; the orchestrator turns them into roadmap
  workstreams.
- **Invoked alone**: `<docs>/audits/maintainability/maintainability-<date>.md`: summary, tools run
  and degraded, trend, hotspot table, prioritized findings, detail by section, a "Heavy
  refactors" section (§11) and an "Applied fixes" section. Update the register if it exists; if the
  roadmap exists, propose the heavy refactors in it as workstreams. Create the branch
  `chore/maintainability-audit-<date>` (or stay on the non-default branch in use,
  `audit-deliverables` §6), commit the report alone on it:
  `docs(audit): maintainability <date>`. The quick wins follow on the same branch.

## 11. Fixes: quick wins only

Propose **one by one**, with validation, only safe and local fixes:
- unused dependencies, exports, files **confirmed** (§8); for a removed dependency, reinstall and
  update the lockfile before checking;
- unused imports and local variables (§4), small duplications inside one module;
- obsolete disabled tests (to delete or re-enable, as the user chooses).

After each fix: the project's build and tests if they exist; if they fail, revert. One Conventional
commit per fix, or per validated batch of the same type (`refactor: remove unused exports`,
`chore(deps): drop unused packages`).

**Heavy refactors are not done here** (splitting a hotspot, breaking a cycle, extracting a module).
They go into the report's "Heavy refactors" section: for each one, the goal, the characterization
tests to write **before** touching it, and the effort. Structural decisions can become ADRs: if the
`dev-workflow` plugin is installed, through `dev-workflow:adr`; otherwise skip.

- **Roadmap present** (`<docs>/debt/roadmap.md`): propose each refactor as a `WS-xx` workstream,
  then, if the user wants, a draft workstream ticket in `docs/tickets/` (format of
  `legacy-takeover` §3.4).
- **No roadmap**: do not invent a `WS-xx` identifier. The refactors stay in the report's "Heavy
  refactors" section and in the register if it exists (Medium rows and above). Offer, as the user
  chooses: create the roadmap (through `maintenance`, on request, or `legacy-takeover` full mode),
  or write draft tickets with `living-specs:ticket-writing` if the `living-specs` plugin is
  installed (otherwise as plain Markdown drafts in `docs/tickets/`), with no workstream identifier.
