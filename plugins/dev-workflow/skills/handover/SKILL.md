---
name: handover
description: Write or refresh HANDOVER.md, a local resume point capturing where work stands so a fresh session can continue. Use to checkpoint progress, after a finished task or an important decision, before a long or risky operation, when pausing or stopping work, or when the user says "/handover", "checkpoint", "save state", "we stop here", "sauvegarde l'état", "on s'arrête là".
---

Maintain `HANDOVER.md` at the root of the working directory as the single source of truth for
resuming work in a fresh session. The plugin's SessionStart hook injects it into the next session,
which resumes from it.

**Overwrite** the file each time (don't append) so it stays a concise, current snapshot, not a log.
Keep it factual and short: it is a resume point, not a report. Write its content in the language
the user works in; the template below gives the structure.

## What to capture

```markdown
# HANDOVER: <project/task>
_Updated: <YYYY-MM-DD HH:mm:ss>_

## Goal
What we are trying to achieve (current feature or task).

## Current state
Where things stand; what works and what does not yet.

## Done
- steps already completed

## Next steps (in order)
- [ ] next concrete step
- [ ] ...

## Key decisions
- choice made: why (so it is not reopened)

## Open questions / blockers
- what is still to be decided

## Files involved
- `path/to/file`: role

## Resume / test
Commands to restart, build, test.
```

Timestamp in `YYYY-MM-DD HH:mm:ss` format, local time, obtained with `date '+%Y-%m-%d %H:%M:%S'`:
never a date typed from memory, never a `DD/MM/YYYY` format, and nothing else on that line (no
"(step 6 written)"): what was done goes under "Done" or "Current state".

## When to update

Keep the file current at all times, not only at the end: a crash or a reboot leaves no chance to
write it afterwards.

- After each finished task.
- After each important decision.
- Before a long or risky operation.
- Always when the user says work stops.

## Rules

- **Never commit** `HANDOVER.md`: it is a local file. Check that it is in `.gitignore` and add it if
  needed. Exception: a project where nothing may be written (the "nothing in the repo" mode of
  `code-audits:legacy-takeover` if the code-audits plugin is installed, a repo that is not yours):
  ignore it through `.git/info/exclude`, which stays local and changes no tracked file.
- **Before each commit**: the plugin's `git-guard` hook blocks a `git commit` while `HANDOVER.md`
  (command directory, repo root or session directory) is older than the last commit. Refresh it,
  then run the commit again. Without `HANDOVER.md`, there is no check. The check can be turned off
  with `DEV_WORKFLOW_GUARD_HANDOVER=0`.
