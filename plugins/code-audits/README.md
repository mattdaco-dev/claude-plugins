# code-audits

Security, performance, maintainability, GDPR and SEO audits, quarterly maintenance passes, legacy
takeover and C4 architecture diagrams for Claude Code. Every audit writes a dated, prioritized
report, then proposes fixes one by one and waits for your approval before each one.

## Install

```
/plugin marketplace add mattdaco-dev/claude-plugins
/plugin install code-audits@mattdaco
```

## Contents

| Kind | Name | What it does |
|---|---|---|
| Skill | `audit-deliverables` | Shared convention for every audit: report paths, frontmatter, severity scale (Critical, High, Medium, Low), finding columns, debt register and roadmap. Loaded by the other skills. |
| Skill | `security-audit` | Whole-project security posture: dependency vulnerabilities, secrets (never displayed), SAST, config and supply chain, abuse controls promised by living specs. |
| Skill | `performance-audit` | Static analysis (dependencies, bundle, build config, back-end anti-patterns) and lab measurements through a Chrome performance trace. |
| Skill | `maintainability-audit` | Technical debt: hotspots (churn × complexity), complexity, duplication, dead code, cycles, test coverage, knowledge concentration; fixes only the quick wins. |
| Skill | `gdpr-audit` | Technical GDPR audit in nine domains (personal data, consent and cookies, rights, retention, security, processors, transfers, by design, AI/LLM) plus a live cookie check. Not legal advice. |
| Skill | `seo-audit` | On-site and technical SEO adapted to the rendering mode: crawl, indexing, on-page, JS rendering, structured data, Core Web Vitals. |
| Skill | `maintenance` | Quarterly maintenance pass over eight zones (deps, security, build, ci, perf, docs, backups, maint), or a single zone. |
| Skill | `legacy-takeover` | Takes over an unfamiliar codebase: a one-page quick overview with a risk map, or a full assessment with parallel audits, a debt register and a phased roadmap. |
| Skill | `c4-architecture` | Builds a C4 model in Structurizr DSL from the code, level by level, validates it and exports a static site. |
| Skill | `dev-server` | Starts the project's dev server and opens Chrome through the Chrome DevTools MCP so Claude can drive the app. |
| Agent | `auditor` | Read-only collection phase of an audit or maintenance zone; returns the complete report as text. Proposed to you, never launched without your consent. It has Bash to run the audit tools, so read-only is enforced by its instructions, not by its tool list. |

## Where reports go

The root is the project's `docs/` by default, or any path you give if nothing should be written in
the repo (then nothing is committed).

```
docs/
├── audits/<type>/<type>-<YYYY-MM-DD>[-<scope>].md   one file per audit (security, performance,
│                                                    maintainability, gdpr, seo, deps, build, ci,
│                                                    docs, backups)
├── debt/
│   ├── register.md      living debt register, TD-xx rows
│   └── roadmap.md       workstreams WS-xx in phases, chosen order
├── maintenance/<YYYY-MM-DD>.md   maintenance pass summary
├── takeover/<YYYY-MM-DD>-quick.md and <YYYY-MM-DD>.md   legacy takeover summaries
└── architecture/workspace.dsl, README.md   C4 model (site/ is generated and git-ignored)
```

Audits run on a `chore/<type>-audit-<date>` branch (never on the default branch), commit the
report alone first, then one commit per fix. The skills never run `git push`.

## External tools

The skills prefer real tools over heuristics and say in each report what actually ran. When a tool
is missing, they offer to install it outside the audited project (`brew`, `pipx`, global install or
a one-off `npx --yes`), never as a project dependency. If you decline, they fall back to a
heuristic and record the tool as "not run".

| Skill | Tools used when present |
|---|---|
| `security-audit` | native audits (`npm audit`, `pnpm audit`, `cargo audit`, `pip-audit`, `bundle audit`, `govulncheck`), `osv-scanner`, `gitleaks` (or `trufflehog`), `semgrep` |
| `performance-audit` | `webpack-bundle-analyzer`, `rollup-plugin-visualizer`, `source-map-explorer`, Chrome DevTools MCP performance trace |
| `maintainability-audit` | `lizard`, `eslint`, PMD and CPD, `radon`, `jscpd`, `knip`, `tsc`, `vulture`, `madge`, `jdeps`, `pydeps`, existing coverage reports |
| `gdpr-audit` | Chrome DevTools MCP (cookies, network requests), `curl` |
| `seo-audit` | `curl`, Chrome DevTools MCP `lighthouse_audit`, Lighthouse CLI, `xmllint` |
| `maintenance` | the above, plus `npm outdated` and equivalents, endoflife.date, `gh` or `glab` for CI state |
| `legacy-takeover` | `git`, endoflife.date, `cloc` if present, `structurizr` through `c4-architecture` |
| `c4-architecture` | `structurizr` (Homebrew formula or the `.war` with Java 21), no Docker |

## Bundled MCP server

The plugin declares the [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
server in `.mcp.json`, started with `npx -y chrome-devtools-mcp@1.12.0 --isolated`, so each session
gets its own throwaway Chrome profile. The version is pinned: a new npm release does not run on your
machine until it has been bumped here. `dev-server`, `performance-audit`, `seo-audit`, `gdpr-audit`
and `c4-architecture` use it. It needs Node.js and Google Chrome. If Node is managed by nvm or a
similar tool and the server fails to connect, `dev-server` explains how to register it with absolute
paths.

## Optional integrations

- **living-specs**: `security-audit` checks the abuse controls declared in the "Abuse and limits"
  section of the feature sheets (`docs/specs/features/`, rules `BR-xx`); `legacy-takeover` uses
  `living-specs:retro-spec` for its functional mapping and `living-specs:ticket-writing` for
  workstream tickets; `c4-architecture` reuses the project glossary and user flows. Without the
  plugin, these steps are skipped or done by hand.
- **dev-workflow**: `legacy-takeover` and `maintainability-audit` record structural decisions with
  `dev-workflow:adr`; `maintenance`, `legacy-takeover`, `gdpr-audit` and `seo-audit` checkpoint
  long runs in `HANDOVER.md` with `dev-workflow:handover`. Without the plugin, these steps are
  skipped.
