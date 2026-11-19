---
name: gdpr-audit
description: "Technical GDPR audit of an application. Shows where the GDPR applies (personal data and special categories, legal basis and consent, cookies, data subject rights, retention, Art. 32 security, processors and third parties, transfers outside the EU, AI/LLM), produces a dated prioritized report with solutions, then iterates point by point. A technical assistance audit, NOT legal advice. Use when the user wants a GDPR audit of an application, or says \"GDPR audit\", \"GDPR compliance\", \"gdpr-audit\", \"audit RGPD\", \"conformité RGPD\". Reused by legacy-takeover."
---

> **Not legal advice.** A **technical assistance** audit: it shows where the GDPR applies in the
> code and proposes technical solutions. Legal and organizational aspects are flagged "to validate
> outside the code". Never present this audit as a guarantee of compliance.

**Supervisory authority**: the one of the controller's main establishment (lead authority,
Art. 56), to **ask the user** and record in the report. The **CNIL developer's GDPR guide** (French
authority) serves as a technical reference; the **EDPB** guidelines apply at EU level. The CNIL's
numeric benchmarks (cookie lifetime, audience measurement exemption, three-stage retention) are
French doctrine: present them as such, and check the position of the chosen authority when it is
not the CNIL.

Goal: show where the GDPR applies, produce a **dated prioritized report with solutions**, then
**iterate point by point**. Hybrid static + live. Audit first, action with consent. **Never run
`git push`.**

## 0. Scope

- `gdpr-audit` with no domain → full audit.
- `gdpr-audit <domain>` → targeted, one domain from §2: `pii` (D1), `consent` (D2, cookies
  included), `rights` (D3), `retention` (D4), `security` (D5), `third-parties` (D6), `transfers`
  (D7), `by-design` (D8), `llm` (D9). `live` runs only the live phase (§3). E.g. `gdpr-audit
  consent` covers D2 and the cookie part of the live phase.
- **API without a front end** (back end only, internal service): D1 to D9 apply; the live phase is
  limited to the API (§3, last point), with no browser and no banner. D2 then looks at how consent
  is recorded and checked on the server, not at cookies.

## 1. Preamble

1. **Context**: if a `HANDOVER.md` exists at the project root, read it. Load `audit-deliverables`.
2. **Detect** the stack and **where personal data lives**: DB schemas, ORM, migrations, services,
   logs, config and environment variables.
3. **Supervisory authority**: ask for it (see top), otherwise record "not specified" and stick to
   the CNIL benchmarks, flagged as such.
4. **Comparison** with the last `gdpr` audit (path per `audit-deliverables` §2), if any: deltas,
   debt.
5. **Best effort**: missing tool or live part impossible → degrade and **note it** (`tools_run` /
   `not_run`); never dress up an estimate, and never present the technical audit as a guarantee of
   legal compliance.
6. **Dedicated branch** in standalone mode (`audit-deliverables` §6): `chore/gdpr-audit-<YYYY-MM-DD>`
   at the latest before the first commit (or the non-default branch already in use). Read-only
   collection can happen before.

## 2. Collection phase (read-only)

**Proposed split, with consent**: one **`auditor`** agent per domain (D1 to D9, or the ones
chosen), launched together in the same message. Announce the split, wait for the user's go-ahead,
otherwise run the domains in sequence. Brief for each: this skill and the domain, the project path,
the scope, the `<docs>` root, the supervisory authority if known, the trigger (`standalone`, or the
orchestrator's with the path of its summary). It returns its findings as text and changes nothing;
the session writes the report. The live part stays in the main session. When called by
`legacy-takeover`, the user's approval of the list of audits counts as consent.

### D1: inventory of personal data and special categories (Art. 4, Art. 9)
Direct **and indirect** identifiers (IP, cookie or device identifier, geolocation). **Special
categories** of Art. 9 (health, biometrics, genetics, religion, sexual orientation, opinions, trade
union membership): they require an Art. 9(2) condition **on top of** an Art. 6 basis. Look for
personal data in **logs, traces, errors, analytics, fixtures**, and in free-text or JSON fields
that hide special categories.

### D2: legal basis and consent (Art. 6, 7), cookies and ePrivacy
One Art. 6 basis **per purpose** (six bases, consent is only one of them). Art. 7 consent: opt-in,
granular, **withdrawable** as easily as it is given, **recorded** (proof). **Non-essential**
cookies and trackers: consent **before** they are set (ePrivacy directive, art. 5(3)); the banner
must **block the tags from firing**, not just hide the interface. The "audience measurement"
exemption is narrow, and its conditions depend on the authority (CNIL benchmarks in §8).

### D3: data subject rights (Art. 15 to 22)
Access and **portability** (structured JSON or CSV export), **real erasure** (all storage, third
parties, backup policy; *soft delete alone = finding*), rectification, restriction, **objection**
(unconditional marketing opt-out). Identity verification on these endpoints.

### D4: minimization and retention (Art. 5(1)(c) and (e))
Collection limited to what is needed; **retention period defined per purpose** (TTL, purge jobs,
log rotation); a **permanent deletion** exists. CNIL benchmark: three-stage retention (active base,
restricted-access archive, deletion or anonymization). No deletion job at all = finding.

### D5: security (Art. 32)
TLS everywhere and HSTS; encryption **at rest**, backups included; **password hashing** (bcrypt,
argon2id, scrypt; flag MD5, SHA1, missing salt, plain text); least privilege and RBAC; **no
hard-coded secret**, including in client bundles; **no personal data in clear in the logs**.

### D6: processors and third parties (Art. 28)
Map **every third party that receives personal data**: analytics, advertising and tag managers,
payment, e-mail and SMS, errors, APM and logs, CDN, maps, support, **LLM APIs**. What is sent, to
whom. Each processor → **data processing agreement** Art. 28(3) (legal aspect, §4). SDKs that
monetize data can be **separate controllers**. Detection: dependency manifests, `<script>` tags,
tag manager config, SDK URLs and initialization.

### D7: transfers outside the EU/EEA (Art. 44 to 49)
Endpoints and regions outside the EU (API URLs, cloud regions such as `us-east-1`, CDN and edge).
Lawfulness: **adequacy** Art. 45 (for the United States, only if the recipient is certified under
the Data Privacy Framework), **standard contractual clauses or BCRs** Art. 46, derogations Art. 49.

### D8: data protection by design and by default (Art. 25), breaches (Art. 33, 34)
Minimizing defaults (opt-in, narrowest visibility, short retention), pseudonymization; **logging
and audit trails** good enough to detect and scope a breach (notification to the authority within
72 h).

### D9: AI and LLM
Personal data interpolated into **prompts or context**? **Prompt and completion logs** that store
it? The provider is a **processor** (Art. 28 agreement), often a **transfer** (inference region),
with **retention, opt-out and no-training** settings to check. **Minimization**: masking or
pseudonymization before sending. Legal basis (often legitimate interest, with a documented
balancing test). Risk of **re-identification** through outputs or embeddings.

## 3. Live phase (site started with `dev-server`, main session)

**Clean browser**: the `dev-server` skill may use a persistent Chrome profile per project, which
keeps cookies and storage from previous sessions. Open each test page in an isolated context
(`new_page` with `isolatedContext`, a new name per scenario), or check that the MCP runs with
`--isolated` and no project `userDataDir`. Measure **before** any interaction with the banner:
- **Cookies** on first load: `document.cookie` (through `evaluate_script`) does not see `HttpOnly`
  cookies. Also read the `Set-Cookie` headers of the responses: `list_network_requests`, then
  `get_network_request` on the document and the third-party requests. Any non-essential cookie set
  **before consent** = breach of ePrivacy art. 5(3). Lifetime beyond the authority's benchmark
  (13 months for the CNIL) = to report.
- **Third-party requests** sent before consent; **localStorage and IndexedDB** (identifiers,
  trackers); **fingerprinting** signals (canvas, WebGL, AudioContext, FingerprintJS).
- Test **"reject"** in a fresh context → no tracker; **"accept"** in another → trackers unlocked.
  A rejection with no effect = finding.
- TLS and mixed content; **personal data in payloads or URLs** sent to third parties.
- **API without a front end**: on a local instance, `curl -si` the endpoints that expose personal
  data: headers (HSTS, `Set-Cookie`), responses that return more data than needed, identifiers in
  URLs.

## 4. Legal and organizational aspects: "outside the code, legal validation"

List without claiming compliance: **record of processing activities** Art. 30, **data processing
agreement** per processor (Art. 28(3)), **information to data subjects** Art. 13 and 14, **data
protection impact assessment (DPIA)** Art. 35, **DPO** Art. 37, legal validity of consents and of
legitimate interest balancing tests.

## 5. Summary and dated report

**Severity**: shared scale from `audit-deliverables` §2, read as a compliance risk. Guide: tracker
before consent, personal data in clear in the logs or sent to a third party without safeguards,
special category without an Art. 9 condition → Critical; no real erasure, no retention period,
transfer without an identified safeguard → High; minimization, non-granular consent → Medium;
hardening → Low.

`<docs>/audits/gdpr/gdpr-<YYYY-MM-DD>.md`, per the **`audit-deliverables`** skill: frontmatter,
common columns first in the table, specific columns after, live part in `## Live`, register
updated if it exists. Disclaimer at the top. Each finding: a plain explanation and a
recommendation. Write the report in the language the user works in; the template below shows the
structure.

```markdown
# GDPR audit: <app>, <YYYY-MM-DD>
> Technical audit, not legal advice.

## Summary
- Supervisory authority: … (or "not specified, CNIL benchmarks")
- Scope and personal data detected: …
- Environment tested (localhost, different from production); real and degraded checks; deltas since <date>
- Exposure empty in a standalone audit (critical paths not provided)

## Prioritized findings
| # | Severity | Effort | Risk | Exposure | Source | Finding | Where | Recommendation | Domain | GDPR article |
|---|---|---|---|---|---|---|---|---|---|---|

## Detail by domain (D1 to D9)

## Live
Cookies (including HttpOnly `Set-Cookie`), third-party requests before consent, reject and accept tested.

## To handle outside the code (legal and organization)
Record of processing, processing agreements, information to data subjects, DPIA, DPO.

## Applied fixes
(standalone mode: one line per fix, finding #, commit, TD-xx closed)
```

- **Called by `legacy-takeover`**: return the collection (read-only), no fixes here; the
  orchestrator writes the file and runs the live part.
- **Invoked alone**: write the report, commit the report alone: `docs(audit): gdpr <date>`. Each
  fix applied afterwards is recorded under "Applied fixes" and closes its register row.

## 6. Fixes one by one (main session, standalone mode)

Order: **clear breaches** (personal data in clear, tracker before consent, no erasure, hard-coded
secret, transfer without safeguards) → **quick wins** (consent, opt-out, retention, masking before
sending to the LLM) → the rest. For each: finding, fix, risk → validation → one Conventional commit
per fix or per validated batch of the same type (`fix(gdpr): gate analytics behind consent`).
**Never push.**

## 7. Resuming across sessions

Keep a running checkpoint in `HANDOVER.md` (with `dev-workflow:handover` if the `dev-workflow`
plugin is installed; otherwise skip): domains done or remaining, findings waiting for a decision.

## 8. False positives not to report (guardrails)

- **Pseudonymized is not anonymized**: pseudonymized data (hashed, with a re-identification key
  somewhere) is still **personal**. Do not "clear" a field because it is hashed. Only
  **irreversible** anonymization takes data out of the GDPR.
- **Consent is not always required**: six bases in Art. 6 (contract, legal obligation, legitimate
  interest…). Do not report "no consent" without looking at the declared basis.
- **Essential cookies are exempt**: session, CSRF, load balancing, cart, storing the consent
  choice.
- **Legitimate interest** Art. 6(1)(f) is valid (with a balancing test), but it opens the right to
  **object** Art. 21: check the opt-out rather than challenge the basis.
- **Audience measurement exemption** is narrow: check the conditions of the chosen authority. CNIL
  benchmarks: single-publisher tool, no cross-referencing with other data, truncated IP, cookie
  lifetime of 13 months at most. Do not assume the exemption.
- **B2B**: business contact data is still personal data, but prospecting rules differ from B2C.
- **Backups**: not purging backups right away after an Art. 17 request is **acceptable** if the
  rotation is documented; the finding is "never any permanent deletion".
- **Synthetic test data** is not personal data (but real data in fixtures = finding).
- **localhost is not production** (TLS, etc.).
