#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash) guarding git commands. Configurable.

- git commit on the default branch (main/master): blocked, unless the repo
  holds a .claude/allow-main-commits marker, or DEV_WORKFLOW_GUARD_MAIN=0.
  A branch created earlier in the same command (checkout -b, switch -c)
  lets the commit through.
- git commit while HANDOVER.md (command dir, repo root or session cwd) is
  older than the last commit: blocked, unless DEV_WORKFLOW_GUARD_HANDOVER=0.
  No HANDOVER.md found: no check.
- git push: allowed, unless DEV_WORKFLOW_BLOCK_PUSH=1.

Heredoc bodies and quoted strings are ignored: a commit message that quotes
a git command triggers nothing.

Exit 2 blocks the call and sends stderr back to Claude; exit 0 lets it run.
Unexpected input or errors always end in exit 0.
"""
import json
import os
import re
import shlex
import subprocess
import sys

# "git" as a command word, optional global options, then the subcommand.
GIT = r"(?:^|[\s;&|(])git(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*\s+"
PUSH = re.compile(GIT + r"push\b")
COMMIT = re.compile(GIT + r"commit\b")
NEW_BRANCH = re.compile(GIT + r"(?:checkout[^;&|\n]*\s-[bB]|switch[^;&|\n]*\s-[cC])\b")
DEFAULT_BRANCHES = {"main", "master"}
MAIN_COMMITS_MARKER = os.path.join(".claude", "allow-main-commits")


def env_flag(name, default):
    """True/False from an env var holding 1/0 (also true/false, yes/no, on/off)."""
    value = os.environ.get(name, "").strip().lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    return default


def block(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def strip_text(command):
    """Drop heredoc bodies and quoted strings, which are data, not commands."""
    command = re.sub(
        r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?:\n|$)",
        "\n",
        command,
        flags=re.S,
    )
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", "''", command)


def target_dir(command, cwd):
    """Directory the git command runs in: last `cd X` before it, or `git -C X`."""
    head = COMMIT.split(command, maxsplit=1)[0]
    directory = cwd
    for match in re.finditer(r"(?:^|[;&|(])\s*cd\s+([^;&|)]+)", head):
        try:
            parts = shlex.split(match.group(1))
        except ValueError:
            continue
        if parts:
            directory = os.path.join(directory, os.path.expanduser(parts[0]))
    c_flag = re.search(r"git\s+-C\s+(\S+)[^;&|]*\bcommit\b", command)
    if c_flag:
        directory = os.path.join(directory, os.path.expanduser(c_flag.group(1).strip("'\"")))
    return os.path.normpath(directory)


def git(directory, *args):
    try:
        result = subprocess.run(
            ["git", "-C", directory, *args], capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def find_handover(directory, cwd):
    """HANDOVER.md in the command's directory, the repo root or the session cwd.

    No walk up the tree: a repo nested in a folder that has its own
    HANDOVER.md must not be checked against it.
    """
    for base in (directory, git(directory, "rev-parse", "--show-toplevel"), cwd):
        if base and os.path.isfile(os.path.join(base, "HANDOVER.md")):
            return os.path.join(base, "HANDOVER.md")
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, UnicodeDecodeError):
        return
    if not isinstance(payload, dict):
        return
    tool_input = payload.get("tool_input")
    raw = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(raw, str) or not raw:
        return
    command = strip_text(raw)
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()

    if PUSH.search(command) and env_flag("DEV_WORKFLOW_BLOCK_PUSH", False):
        block(
            "git push is blocked in this environment (DEV_WORKFLOW_BLOCK_PUSH=1): "
            "commit locally and ask the user to push."
        )

    if not COMMIT.search(command):
        return

    directory = target_dir(raw, cwd)
    if not os.path.isdir(directory):
        return

    if env_flag("DEV_WORKFLOW_GUARD_MAIN", True):
        branch = git(directory, "symbolic-ref", "--short", "HEAD")
        creates_branch = NEW_BRANCH.search(COMMIT.split(command, maxsplit=1)[0])
        root = git(directory, "rev-parse", "--show-toplevel")
        allows_main = root and os.path.isfile(os.path.join(root, MAIN_COMMITS_MARKER))
        if branch in DEFAULT_BRANCHES and not creates_branch and not allows_main:
            block(
                f"Commit on '{branch}' is blocked: create a <type>/<slug> branch "
                "first (for example feat/my-change), then commit there. To allow "
                "commits on the default branch in this repo, add a "
                ".claude/allow-main-commits file; to turn this check off, set "
                "DEV_WORKFLOW_GUARD_MAIN=0."
            )

    if env_flag("DEV_WORKFLOW_GUARD_HANDOVER", True):
        handover = find_handover(directory, cwd)
        last_commit = git(directory, "log", "-1", "--format=%ct")
        if handover and last_commit and os.path.getmtime(handover) < int(last_commit):
            block(
                f"{handover} has not been updated since the last commit: refresh "
                "it (handover skill), then commit again. To turn this check off, "
                "set DEV_WORKFLOW_GUARD_HANDOVER=0."
            )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
    sys.exit(0)
