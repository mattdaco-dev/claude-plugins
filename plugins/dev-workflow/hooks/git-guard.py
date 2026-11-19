#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash) guarding git commands. Configurable.

- git commit on the default branch (main/master): blocked, unless the repo
  holds a .claude/allow-main-commits marker, or DEV_WORKFLOW_GUARD_MAIN=0.
  A checkout/switch earlier in the same command counts: creating a branch
  (checkout -b, switch -c) lets the commit through, switching to main/master
  does not.
- git commit while HANDOVER.md (command dir, repo root, or session cwd when
  it is the same repo) is older than the user's last commit: blocked, unless
  DEV_WORKFLOW_GUARD_HANDOVER=0. Commits by others (pulled in) do not count.
  No HANDOVER.md found: no check.
- git push: allowed, unless DEV_WORKFLOW_BLOCK_PUSH=1.

Heredoc bodies and quoted strings are ignored: a commit message that quotes
a git command triggers nothing. The flip side is that `bash -c "git commit"`
or a git alias (`git ci`) is not seen: this is a guard against mistakes, not
a security boundary.

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
SWITCH = re.compile(GIT + r"(checkout|switch)\b([^;&|\n)]*)")
CREATE_FLAGS = {"-b", "-B", "-c", "-C", "--orphan", "--create", "--force-create"}
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


def branch_after_switch(head, current):
    """Branch the commit lands on, given the checkout/switch calls before it.

    Returns (branch, created): created is True when the last relevant call
    creates a branch. A checkout of a path or of an unknown ref leaves the
    current branch unchanged, except a switch to main/master.
    """
    branch, created = current, False
    for match in SWITCH.finditer(head):
        try:
            args = shlex.split(match.group(2))
        except ValueError:
            continue
        if "--" in args:
            continue
        flag = next((a for a in args if a in CREATE_FLAGS), None)
        if flag:
            rest = args[args.index(flag) + 1:]
            branch, created = (rest[0] if rest else None), True
            continue
        targets = [a for a in args if not a.startswith("-")]
        if targets and targets[0] in DEFAULT_BRANCHES:
            branch, created = targets[0], False
    return branch, created

def find_handover(directory, cwd):
    """HANDOVER.md in the command's directory, the repo root or the session cwd.

    No walk up the tree: a repo nested in a folder that has its own
    HANDOVER.md must not be checked against it. The session cwd only counts
    when it belongs to the same repo as the command's directory.
    """
    root = git(directory, "rev-parse", "--show-toplevel")
    bases = [directory, root]
    if root and git(cwd, "rev-parse", "--show-toplevel") == root:
        bases.append(cwd)
    for base in bases:
        if base and os.path.isfile(os.path.join(base, "HANDOVER.md")):
            return os.path.join(base, "HANDOVER.md")
    return None

def last_own_commit(directory):
    """Timestamp of the last commit by the configured user (all commits if unset)."""
    email = git(directory, "config", "user.email")
    if email:
        return git(directory, "log", "-1", "--fixed-strings", f"--author=<{email}>", "--format=%ct")
    return git(directory, "log", "-1", "--format=%ct")


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
        branch, created = branch_after_switch(
            COMMIT.split(command, maxsplit=1)[0],
            git(directory, "symbolic-ref", "--short", "HEAD"),
        )
        root = git(directory, "rev-parse", "--show-toplevel")
        allows_main = root and os.path.isfile(os.path.join(root, MAIN_COMMITS_MARKER))
        if branch in DEFAULT_BRANCHES and not created and not allows_main:
            block(
                f"Commit on '{branch}' is blocked: create a <type>/<slug> branch "
                "first (for example feat/my-change), then commit there. To allow "
                "commits on the default branch in this repo, add a "
                ".claude/allow-main-commits file; to turn this check off, set "
                "DEV_WORKFLOW_GUARD_MAIN=0."
            )

    if env_flag("DEV_WORKFLOW_GUARD_HANDOVER", True):
        handover = find_handover(directory, cwd)
        last_commit = last_own_commit(directory)
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
