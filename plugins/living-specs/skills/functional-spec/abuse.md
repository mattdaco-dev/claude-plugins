# Abuse and limits: grid per feature

Adapted from `product-launch/references/abuse-and-security.md` in
[geoffreycrofte/saas-launch-skillset](https://github.com/geoffreycrofte/saas-launch-skillset) by
Geoffrey Crofte, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes
were made: rewritten and reorganised for business applications.

Reference loaded on demand by `grill-me` (abuse track), by this skill (the "Abuse and limits"
section of the feature sheet) and by `ticket-writing` (blocked-case scenarios). If the code-audits
plugin is installed, `code-audits:security-audit` also reads it to check the controls promised by
the specs; otherwise skip that part.

## 1. The two questions

For each feature, each action that writes, reads in bulk, sends or calls a third party:

1. **How would a user, a script or an ill-intentioned colleague misuse it?**
   Also think of the compromised legitimate account and of the hurried user who repeats the same
   action.
2. **What does this misuse cost when repeated a thousand times?** In money (paid calls, AI,
   emails), in data (leak, extraction, alteration), for other users (spam, harassment), for
   reputation and email deliverability, in legal exposure (GDPR).

Design the limit so that **nobody does it a thousand times**, not so that nobody does it twice.

## 2. Principles

- **Server-side, or it doesn't exist.** A limit, a permission or a cap checked only in the browser
  is a suggestion.
- **A limit reached is a flow.** The user sees a message (`MSG-xx`) that says what to do; the case
  has its scenario in the ticket.
- **Figures are business decisions.** Cap, time window, export volume: until the business has
  settled them, they are a `Q-xxx` with an assumption, not a rule.
- **An accepted risk is written with its reason** ("volume too low", "identified and logged internal
  users"), so the debate is not reopened.
- **A log is a processing of personal data**: who is tracked, for how long, who reads it (if the
  code-audits plugin is installed, `code-audits:gdpr-audit` covers it).

## 3. Common patterns

Business applications first, public cases next. The listed controls are starting points to settle,
not a list to apply wholesale.

| Feature | Typical abuse | Default controls |
|---|---|---|
| Read or change an object by its identifier | Change the identifier to reach an object of another scope (customer, branch, team), including through a child object (attachment, comment) | Check server-side that the object and its children are in the caller's scope; same response for "does not exist" and "forbidden" |
| Roles, permissions, assignment | Grant oneself a role, change one's own role through a generic update, remove a superior | Allow-list of editable fields; the caller must have strictly more rights than the target; a single permission mapping table; a removal takes effect immediately |
| Export, print, download | Mass extraction by a compromised account or a leaving employee | Same scope as the screen; cap on volume and frequency; log; alert above a threshold |
| Search, autocomplete, existence check | Enumerate customers, contracts or accounts | Results bounded to the scope; minimum input before searching; rate limit; identical message whether the object exists or not |
| Bulk action (validation, reminder, grouped deletion) | A mistake or an abuse multiplied by the number of objects | Cap per batch; confirmation that states the count; undo or recycle bin; log |
| File import or upload | Booby-trapped, huge or disguised file; formula in a CSV that runs when opened in a spreadsheet | Allowed types checked on the content; maximum size; antivirus scan if available; files served from a separate origin; cells starting with `= + - @` neutralized on export |
| Free text shown to others (comment, note, name) | Injected script, booby-trapped link, abusive content | Escaping by default; sanitized markup; reporting and moderation if the audience is large |
| URL supplied by the user (import from link, webhook, preview) | Make the server call an internal address or the cloud metadata endpoint (SSRF) | Resolve and check each address, at each redirect; reject private ranges; fail closed if resolution fails; call from an isolated network |
| Notification or email triggered by the user (invitation, share, reminder) | Spam or harassment sent from our domain | Fixed templates, no free subject; cap per day and per recipient; unsubscribe |
| AI feature | Exploding cost; hidden instruction in a processed document; leak through the model's tools; wrong answer taken as true | Per-user budget enforced server-side; document content treated as data; tools limited to the user's scope; guardrails from the AI assistance section |
| Login, forgotten password | Brute force; finding out whether an account exists; burst of resets | Rate limit; identical response; a reset revokes sessions and tokens |
| API key, integration token | Key shared, leaked or used outside its scope | Hashed at rest, shown once; scope; last-used date; revocation; limit per key |
| Sign-up, free account (public) | Fake accounts in bulk, disposable addresses | Accessible captcha; honeypot field; address verification; limit per IP address |
| Anonymous public form (contact, quote, simulator) | Spam; cost per submission (email, AI, third-party call) | Accessible captcha; limits per IP then global; global budget; degraded service rather than outage |
| Free-plan quota | Delete then recreate to stay under the cap | Count creations over a period, not existing objects |

## 4. What the decision becomes in the sheet

Each abuse discussed has a row in the "Abuse and limits" section of the feature sheet:

- **controlled**: the control is written as a rule `BR-xx`, one testable sentence ("An export
  contains at most 5,000 rows."), with the `MSG-xx` shown when the limit is reached and, for a
  permission, its row in Roles and permissions;
- **accepted**: the reason, in one sentence;
- **figure or control not settled**: a `Q-xxx` with the assumption, never a Proposed rule.

No abuse surface (viewing one's own data, no volume, nothing sent): one row that says so with the
reason. Section not discussed: the question "how could this feature be misused?" goes into
`questions.md`.
