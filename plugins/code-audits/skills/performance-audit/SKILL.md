---
name: performance-audit
description: "Performance audit of a project. Static analysis (heavy dependencies, bundle size, build config, anti-patterns, back end included) and, for a web app, lab measurements through a performance trace from the Chrome DevTools MCP (dev-server skill). Use when the user wants a performance audit, or says \"performance audit\", \"analyze performance\", \"why is the app slow\", \"audit de performance\", \"analyse les perfs\". Reused by maintenance (perf zone) and legacy-takeover, and in collection-only mode by seo-audit."
---

Goal: audit the **performance** of a project, first statically, then, for a web app, with lab
measurements on the key pages. Usable on its own, called by `maintenance` (`perf` zone) or
`legacy-takeover`, or in collection-only mode by `seo-audit`. **Never run `git push`.**

## 0. Method: real tools first

- Measure with a tool when one gives the answer (bundle analyzer, browser trace); estimating by
  reading the code comes last. **State what ran and what was estimated**: `tools_run` / `not_run`
  in the frontmatter, Source column of each finding (`audit-deliverables` §2).
- Presence of an npm tool: `npx --no <tool> --version`. Missing: offer a one-off run
  (`npx --yes <tool>`, npm cache, nothing in the project) or a global install, after consent;
  never `npm i -D` and never a change to the audited project's manifest or lockfile.
- **Called through the `auditor` agent**: no install, no build, no live part. Static fallback,
  tools listed in `not_run`, live measurements and installs listed under "To do in the main
  session".

## 1. Static analysis (always)

- **Dependency weight**: heavy packages, duplicates (several versions of the same lib), unused
  dependencies, lighter alternatives.
- **Bundle** (front end): size of bundles and chunks from an existing report or an analyzer
  (`webpack-bundle-analyzer`, `rollup-plugin-visualizer`, `source-map-explorer` on an existing
  build), code splitting, effective tree-shaking. With no build and no report: an estimate, noted
  as such.
- **Build config**: minification, compression, caching, production mode, compiler options.
- **Anti-patterns**: large eager imports, expensive loops on hot paths, blocking synchronous work.
- **Back end** (and any app without a front end): only this part applies, with no bundle and no
  browser measurement. Look for N+1 queries, missing pagination or indexes on frequent queries,
  network calls in series that could run in parallel, no cache on repeated reads, badly sized
  connection pools, heavy serialization, startup cost. A load test (k6, wrk, Gatling) is out of
  scope unless asked: note it as "to measure" with what should be measured.

## 2. Live measurements (web app, main session)

1. **Key pages**: the ones the user names, or the entry points of the critical paths given in the
   brief (`maintenance`, `legacy-takeover`). Otherwise ask; with no answer, the home page and one
   representative per page type, and say so.
2. **Production build served locally, preferably**: `vite build && vite preview`,
   `next build && next start`, `ng build` then a static server on the output folder, etc. The
   build writes into the project's output folder: ask before running it. Otherwise, the dev server
   through the **`dev-server`** skill, and note the bias in the report: no minification, unbundled
   modules, HMR and sourcemaps, often no compression. The numbers are then pessimistic and not
   comparable with a run on a production build.
3. **Performance trace** with the Chrome DevTools MCP (bundled with this plugin, started by
   `dev-server`): for each page, `navigate_page`, then `performance_start_trace` (`reload: true`,
   `autoStop: true`); detail the reported insights with `performance_analyze_insight` (e.g.
   `LCPBreakdown`, `RenderBlocking`, `DocumentLatency`). Record LCP, CLS, TBT if provided,
   render-blocking resources, transferred weight.
4. **Conditions**: apply a modest mobile profile with `emulate` (`cpuThrottlingRate: 4`,
   `networkConditions: "Slow 4G"`) and note it; ideally three runs per page, median kept,
   otherwise say there was only one.
5. The MCP's `lighthouse_audit` **excludes the Performance category**: it is not used here. It
   covers accessibility, SEO and best practices, and `seo-audit` is the one that uses it.
6. No web app, or the server cannot start: stay on the static part and **note it**.

**Lab or field**: these are lab measurements, on a given machine and network. They do not tell
whether the site "passes Core Web Vitals", a verdict that comes from field data (CrUX, Search
Console, RUM, 75th percentile). INP needs real interactions: a load trace does not measure it, TBT
is only a proxy. Never present a lab run as a field result.

## 3. Trend

Compare with the last `performance` audit (path per `audit-deliverables` §2): metrics per page,
bundle sizes, to flag **regressions**. Only compare runs made under the same conditions
(production build or dev, emulation profile); otherwise say so.

## 4. Severity

Shared scale from `audit-deliverables` §2. Guide: key page unusable on a modest mobile (lab LCP
> 4 s on a production build), N+1 on a critical path → High; heavy bundle or avoidable dependency,
no cache or compression → Medium; micro-optimization → Low. Critical stays rare: outage or timeout
under normal load.

## 5. Output

Deliverables per the **`audit-deliverables`** skill (path, frontmatter, common columns, debt
register), type `performance`; measurements go in the `## Live` section, with the conditions
(build or dev, emulation, number of runs). Write the report in the language the user works in. For
each finding: severity, effort, risk, location, actionable recommendation.

- **Called by `maintenance` or `legacy-takeover`**: return the collection (read-only). The
  orchestrator writes the file, runs the live part and proposes the fixes.
- **Called by `seo-audit`**: collection only, on the pages and parts the calling audit asks for
  (static, live trace, or both). Return the findings and measurements to the calling audit, which
  puts them in its own report: no `performance` file, no register update, no fixes.
- **Invoked alone** (`audit-deliverables` §6):
  1. Branch `chore/performance-audit-<YYYY-MM-DD>` at the latest before the first commit (or the
     non-default branch already in use).
  2. Write `<docs>/audits/performance/performance-<YYYY-MM-DD>.md`, update the register if it
     exists, commit the report alone: `docs(audit): performance <date>`.
  3. Propose the fixes **one by one**, with validation; one commit per fix or per validated batch
     of the same type, recorded under "Applied fixes", `TD-xx` row closed.
  4. **Never run `git push`.**
