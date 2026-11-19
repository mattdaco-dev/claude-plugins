---
name: seo-audit
description: "On-site and technical SEO audit of a website (general purpose, adapted to the rendering mode): crawlability, indexability, on-page, JS rendering, structured data, Core Web Vitals. Hybrid static + live (reuses dev-server, the Lighthouse SEO audit of the Chrome DevTools MCP, and performance-audit in collection-only mode). Produces a dated prioritized report, then proposes fixes one by one. Use when the user wants an SEO audit, or says \"seo-audit\", \"SEO audit\", \"check the SEO\", \"search engine optimization\", \"audit SEO\", \"audit de référencement\". Different from performance-audit (which it reuses for Core Web Vitals). Reused by legacy-takeover."
---

Goal: audit the **on-site and technical** SEO of a website, in **hybrid** mode (static analysis of
the code and live audit of the rendered site), **adapted to the detected rendering mode**.
Read-only audit first, **dated prioritized report** next, then **fixes one by one**. **Never run
`git push`.** Off-page SEO (backlinks, authority, rankings) cannot be measured from the code: it is
handled as "to check elsewhere".

This skill carries the SEO expertise: each finding explains the *what* and the *why*, in a way
that teaches. The thresholds and rules below come from primary sources (Google Search Central,
web.dev, Lighthouse, schema.org).

## 0. Scope

- `seo-audit` with no zone → full audit.
- `seo-audit <zone>` → targeted, one zone among: `technical` (crawl, indexing, i18n), `on-page`,
  `structured-data`, `rendering` (raw HTML and rendered DOM, status codes), `cwv` (Core Web
  Vitals). These are the subsections of §3 and §4 and the "Detail by zone" sections of the report.

## 1. Preamble

1. **Context**: if a `HANDOVER.md` exists at the project root, read it at the start of the
   session. Load `audit-deliverables`.
2. **Detect the stack and rendering mode**: SSR/SSG (Next, Nuxt, SvelteKit, Astro…), **pure SPA
   (CSR)**, static site, or classic server rendering. Rendering drives the first risk: *is the
   content in the initial HTML, or only after the JS runs?*
3. **Comparison** with the last `seo` audit (path per `audit-deliverables` §2), if any: deltas,
   carried-over debt.
4. **Best effort**: if a tool is missing, **offer to install it** (§2), otherwise degrade and
   **note it** (`tools_run` / `not_run`); never pass an estimate off as a check.
5. **Dedicated branch** in standalone mode (`audit-deliverables` §6): `chore/seo-audit-<YYYY-MM-DD>`
   at the latest before the first commit (or the non-default branch already in use). Read-only
   collection can happen before.

## 2. Tools

- **Reading the code**: `Grep`, `Read` on templates, layouts, routing config, `robots.txt`,
  sitemap, `<head>` components.
- **`curl`** (live): raw HTML (`curl -s <url>`), status codes and redirects (`curl -sIL <url>`),
  `X-Robots-Tag` headers, served `robots.txt` and sitemap.
- **Chrome DevTools MCP** (bundled with this plugin), started by the `dev-server` skill:
  `navigate_page`, `evaluate_script` (rendered DOM, `<head>` tags after hydration),
  `list_network_requests`, and **`lighthouse_audit`** for the **SEO category** (plus accessibility
  and best practices). This tool excludes the Performance category.
- **`performance-audit` in collection-only mode** (its §5) for lab Core Web Vitals (performance
  trace): no second report, no register, no fixes on its side.
- **Lighthouse CLI**, optional and after consent, one-off run outside the project:
  `npx --yes lighthouse <url> --only-categories=seo --output=json --quiet --chrome-flags="--headless"`.
- **Validators**: `xmllint --noout sitemap.xml` (well-formed XML), Schema Markup Validator
  (https://validator.schema.org, general correctness) and Rich Results Test
  (https://search.google.com/test/rich-results, Google eligibility). For a local site, paste the
  JSON-LD, with no sensitive data.

## 3. Static pass (read-only, code)

### Technical: crawl and indexing
- `robots.txt`: present in the code, valid syntax, **does not block** the CSS and JS needed for
  rendering, a `Sitemap:` line present. The 200 status when served is checked in the live pass
  (§4). robots.txt controls **crawling**, not **indexing**: a blocked page can stay indexed (URL
  only), and a `noindex` on a blocked page is **never seen**.
- `sitemap.xml`: valid XML, **canonical URLs only** (no noindex, redirects or 4xx), correct
  `<lastmod>`, split beyond 50,000 URLs or 50 MB.
- meta robots and `X-Robots-Tag`: no stray `noindex` on pages meant to rank. To deindex, use
  `noindex` on a **crawlable** page (not robots.txt).
- `rel=canonical`: one per page, **absolute**, self-referencing on canonical pages, consistent with
  the sitemap and internal links. Be wary of canonicals **injected or contradicted by JS**.
- **i18n**: **reciprocal** `hreflang` (with `x-default`), valid language and region codes.

### On-page
- Unique and descriptive `<title>`. Length: a **soft** criterion (flag a *truncation risk* around
  50 to 60 characters, **not** a violation).
- meta description present and unique (around 150 to 160 characters, soft, Google may rewrite it).
- Consistent heading hierarchy (several `<h1>` are **tolerated** in HTML5: advice, not an error).
- Semantic HTML; descriptive `alt` (`alt=""` is **valid** for a decorative image); internal links
  as **real `<a href>`** (not `onClick` or `router.push` alone) with descriptive anchors.
- Open Graph and Twitter: `og:title`, `og:description`, `og:image` (absolute, at least 1200×630),
  `og:url`, `og:type`, `twitter:card=summary_large_image`.

### Structured data
**JSON-LD** preferably, types suited to the intent (`Article`/`BlogPosting`,
`Product`+`Offer`+`AggregateRating`, `BreadcrumbList`, `FAQPage`, `Organization`,
`LocalBusiness`…), **consistent with the visible content** (no markup without content).

## 4. Live pass (site started with `dev-server`, main session)

For **one representative per page type** detected (home, listing, detail or article, contact…):

### Rendering
- **Raw HTML and rendered DOM**: `curl -s <url>` on one side, rendered DOM (Chrome DevTools MCP)
  on the other. If content, title, canonical, meta, structured data or links appear **only** in the
  rendered DOM → **CSR at risk** (Bing partially, social previews and AI crawlers do not run JS).
  This is the key indicator of the rendering mode.
- **Status codes and redirects**: `curl -sI <url>` → 200 on live pages, **301** in a single hop (no
  chains), **real 404 or 410** (no SPA **soft-404** returning 200).
- **Served files**: `robots.txt` and sitemap answer 200 with the right `Content-Type`.

### Lighthouse SEO
The MCP's `lighthouse_audit` on each representative page: score and failed SEO audits (blocked
indexing, non-crawlable links, `hreflang`, `alt`, HTTP status…).

### Core Web Vitals
Through `performance-audit` in collection-only mode (performance trace). "Good" thresholds:
**LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1**. A lab trace gives LCP and CLS, and TBT as a proxy for
INP. **INP** and the official Core Web Vitals verdict come from the **field** (CrUX, 75th
percentile). **Never** conclude "passes Core Web Vitals" from a lab run; cross-check with CrUX or
Search Console when available.

### Structured data validation
Schema Markup Validator and Rich Results Test (§2) on the types present.

## 5. Off-page (not measured, "to check elsewhere")

Backlinks, domain authority, rankings, index coverage: to check in **Google Search Console** and
dedicated tools (Ahrefs, Semrush). Say **what** to look at and **where**, without claiming to have
measured it.

## 6. Severity

Shared scale from `audit-deliverables` §2. SEO guide: key page that cannot be indexed (stray
noindex, content missing from the HTML on a site meant to be indexed, widespread soft-404) →
Critical; broken canonical, duplicate title on key pages, non-crawlable internal links → High;
invalid structured data, missing meta description → Medium; title truncation, heading order →
Low.

## 7. Summary and dated report

`<docs>/audits/seo/seo-<YYYY-MM-DD>.md`, per the **`audit-deliverables`** skill: frontmatter,
common columns first in the table, specific columns after, live part in `## Live`, register
updated if it exists. Each finding: a plain explanation and a recommendation. Write the report in
the language the user works in; the template below shows the structure.

```markdown
# SEO audit: <site>, <YYYY-MM-DD>

## Summary
- Detected stack and rendering mode: …
- Environment tested (localhost or local build, different from production): …
- Checks actually run and degraded checks: …
- Deltas since the previous run (<date>): …
- Exposure empty in a standalone audit (critical paths not provided)

## Prioritized findings
| # | Severity | Effort | Risk | Exposure | Source | Finding | Where | Recommendation | Zone | SEO impact |
|---|---|---|---|---|---|---|---|---|---|---|

## Detail by zone
### Technical (crawl, indexing, i18n) · On-page · Rendering · Structured data · Core Web Vitals

## Live
Per page: raw and rendered HTML, status codes, Lighthouse SEO score, lab CWV and conditions.

## Off-page (to check elsewhere)

## Applied fixes
(standalone mode: one line per fix, finding #, commit, TD-xx closed)
```

- **Called by `legacy-takeover`**: return the collection (read-only), no fixes here; the
  orchestrator writes the file and runs the live part.
- **Invoked alone**: write the report, commit the report alone: `docs(audit): seo <date>`. Each
  fix applied afterwards is recorded under "Applied fixes" and closes its register row.

## 8. Fixes one by one (main session, standalone mode)

Order: **indexing blockers** (stray noindex, content not rendered on the server, soft-404, broken
canonical) → **quick wins** (title, meta, alt, links, structured data) → **Core Web Vitals and
performance** → the rest. For each: finding, fix, risk → validation → apply → one Conventional
commit per fix or per validated batch of the same type (`fix(seo): …`,
`feat(seo): add Product JSON-LD`). **Never push.**

## 9. Resuming across sessions

Keep a running checkpoint in `HANDOVER.md` (with `dev-workflow:handover` if the `dev-workflow`
plugin is installed; otherwise skip): pages and zones done or remaining, findings waiting for a
decision.

## 10. False positives not to report (guardrails)

- **localhost is not production**: do not report "no HTTPS" on localhost; local CWV are not field
  CWV.
- **robots.txt is not noindex**: do not say "blocked by robots.txt so deindexed", do not recommend
  robots.txt to deindex.
- **Title and description length**: a soft criterion, flag truncation, not a "violation".
- **Several `<h1>`, heading order**: advice, not an error.
- **`rel=next/prev`**: do not report it as missing (dropped by Google); do not point the canonical
  of paginated pages to page 1.
- **`alt=""`**: valid for a decorative image.
- **Staging and preview** legitimately in `noindex` or behind authentication: not a production
  defect.
- **Dynamic rendering**: **deprecated** by Google, recommend SSR or SSG, never dynamic rendering.
- **FID**: INP replaced FID as a Core Web Vital on 12 March 2024. Do not measure, report or
  recommend optimizing FID.
- Do not claim "CWV OK" from a single lab run.
