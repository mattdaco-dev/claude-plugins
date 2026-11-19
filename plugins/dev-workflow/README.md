# dev-workflow

Session handover, architecture decision records, role-named subagents and a configurable git guard
for Claude Code.

## Install

```
/plugin install dev-workflow --marketplace mattdaco-dev/claude-plugins
```

Or add the marketplace once with `/plugin marketplace add mattdaco-dev/claude-plugins`, then
`/plugin install dev-workflow@mattdaco`.

## Contents

| Kind | Name | What it does |
|---|---|---|
| Skill | `handover` | Writes or refreshes `HANDOVER.md`, a local resume point for the next session. |
| Skill | `adr` | Keeps an architecture decision log (one file per decision), reusing an existing register; does nothing without a register or a request. |
| Agent | `debugger` | Reproduces and diagnoses a bug, failing test or broken build; fixes only if the brief says so. |
| Agent | `researcher` | Read-only research in code or external docs, returns a sourced conclusion. |
| Agent | `implementer` | Carries out a bounded coding task on a fixed set of files and reports what it changed and verified. |
| Hook | `session-handover.sh` (SessionStart) | Injects `HANDOVER.md` from the working directory, with the rules to resume from it and keep it current; silent when there is none. |
| Hook | `git-guard.py` (PreToolUse on Bash) | Blocks commits on `main`/`master` and commits made while `HANDOVER.md` is stale; can also block `git push`. |

The three agents exist so that delegated work shows its role in the running-agent list instead of
`general-purpose`.

## HANDOVER.md workflow

1. Run `/handover` (or ask for a checkpoint) to write `HANDOVER.md` at the root of the working
   directory: goal, current state, done, next steps, key decisions, open questions, files, how to
   resume.
2. Claude keeps it current after each finished task or important decision and before a long or
   risky operation, overwriting it each time.
3. The file is local: it is never committed and should be listed in `.gitignore` (or
   `.git/info/exclude`). The SessionStart hook warns when git does not ignore it.
4. The next session starts with the file injected into context and resumes from it.
5. Before each commit, `git-guard` checks that `HANDOVER.md` is newer than the last commit, so the
   resume point never lags behind the history.

## git-guard configuration

| Setting | Default | Effect |
|---|---|---|
| `DEV_WORKFLOW_GUARD_MAIN` | on | `git commit` on `main`/`master` is blocked. Set to `0` to turn the check off everywhere. A branch created earlier in the same command (`git checkout -b`, `git switch -c`) lets the commit through. |
| `.claude/allow-main-commits` | absent | File at the repo root. When present, commits on the default branch are allowed in that repo only. |
| `DEV_WORKFLOW_GUARD_HANDOVER` | on | `git commit` is blocked while `HANDOVER.md` (command directory, repo root or session directory) is older than the last commit. Set to `0` to turn it off. No `HANDOVER.md`: no check. |
| `DEV_WORKFLOW_BLOCK_PUSH` | off | Set to `1` to block every `git push`, so Claude commits locally and leaves pushing to you. |

Set the variables in your shell profile or in the `env` block of `settings.json`. Heredoc bodies
and quoted strings are ignored, so a commit message that quotes a git command triggers nothing.
When blocking, the hook exits with code 2 and explains why on stderr; on any other input it exits
with 0.

## Testing the guard

Pipe a hook payload into the script from a throwaway repository:

```sh
cd "$(mktemp -d)" && git init -q -b main && git commit -q --allow-empty -m init
echo '{"cwd":"'"$PWD"'","tool_input":{"command":"git commit -m x"}}' \
  | python3 /path/to/dev-workflow/hooks/git-guard.py; echo $?          # 2: blocked on main
echo '{"cwd":"'"$PWD"'","tool_input":{"command":"git push"}}' \
  | DEV_WORKFLOW_BLOCK_PUSH=1 python3 /path/to/dev-workflow/hooks/git-guard.py; echo $?   # 2
```

Exit code 2 means blocked, 0 means allowed.
