#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash) guarding git commands. Configurable.

- git commit on the default branch (main/master): blocked, unless the repo
  holds a .claude/allow-main-commits marker, or DEV_WORKFLOW_GUARD_MAIN=0.
  A checkout/switch earlier in the same command counts: creating a branch
  (checkout -b, switch -c) lets the commit through, switching to main/master
  does not.
- git commit while HANDOVER.md (command dir, repo root, or session cwd when
  it is the same repo) is older than the author date of the user's last
  commit: blocked, unless DEV_WORKFLOW_GUARD_HANDOVER=0. Commits by others
  (pulled in) do not count; an --amend or a rebase keeps the author date.
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
import time

# One shell word: double-quoted, single-quoted or bare.
ARG = r"(?:\"[^\"]*\"|'[^']*'|\S+)"
# "git" as a command word, optional global options, then the subcommand.
GIT = r"(?:^|[\s;&|(])git(?:\s+(?:-[Cc]\s+" + ARG + r"|--[\w-]+(?:=" + ARG + r")?))*\s+"
# (?![\w-]): "commit" but not "commit-tree" or "commit-graph".
PUSH = re.compile(GIT + r"push(?![\w-])")
COMMIT = re.compile(GIT + r"commit(?![\w-])")
SWITCH = re.compile(GIT + r"(checkout|switch)\b([^;&|\n)]*)")
CREATE_FLAGS = {"-b", "-B", "-c", "-C", "--orphan", "--create", "--force-create"}
DEFAULT_BRANCHES = {"main", "master"}
MAIN_COMMITS_MARKER = os.path.join(".claude", "allow-main-commits")
# hooks.json gives the hook 10 s: stop calling git after 8 s and let the
# command through rather than being killed by the timeout.
DEADLINE = time.monotonic() + 8
# Commits scanned to find the user's last one: bounds the walk on a large
# repository where the user has not committed recently.
OWN_COMMIT_WINDOW = 200


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
    """Blank heredoc bodies and quoted strings, which are data, not commands.

    Same length as the input, quotes kept: a match position in the result
    points at the same text in the raw command, so arguments can be read
    back from it.
    """
    def blank(match):
        return re.sub(r"[^\n]", " ", match.group(0))

    def blank_inside(match):
        text = match.group(0)
        return text[0] + " " * (len(text) - 2) + text[-1]

    command = re.sub(
        r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\s*(?:\n|$)",
        blank,
        command,
        flags=re.S,
    )
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", blank_inside, command)


def first_word(raw, start, end):
    """First shell word of raw[start:end], quotes removed."""
    try:
        parts = shlex.split(raw[start:end])
    except ValueError:
        return None
    return parts[0] if parts else None


def target_dir(raw, command, cwd):
    """Directory the git command runs in: last `cd X` before it, or `git -C X`.

    `command` is strip_text(raw): matches are found there, so a `cd` inside a
    quoted string is ignored, and the argument is read back from `raw`.
    """
    commit = COMMIT.search(command)
    head_end = commit.start() if commit else len(command)
    directory = cwd
    for match in re.finditer(r"(?:^|[;&|(])\s*cd\s+([^;&|)]+)", command[:head_end]):
        word = first_word(raw, *match.span(1))
        if word:
            directory = os.path.join(directory, os.path.expanduser(word))
    c_flag = re.search(r"git\s+-C\s+(" + ARG + r")[^;&|]*\bcommit\b", command)
    if c_flag:
        word = first_word(raw, *c_flag.span(1))
        if word:
            directory = os.path.join(directory, os.path.expanduser(word))
    return os.path.normpath(directory)


def git(directory, *args):
    remaining = DEADLINE - time.monotonic()
    if remaining <= 0:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", directory, *args],
            capture_output=True, text=True, timeout=min(5, remaining),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def branch_after_switch(raw, head, current):
    """Branch the commit lands on, given the checkout/switch calls before it.

    Returns (branch, created): created is True when the last relevant call
    creates a branch. A checkout of a path or of an unknown ref leaves the
    current branch unchanged, except a switch to main/master.
    """
    branch, created = current, False
    for match in SWITCH.finditer(head):
        try:
            args = shlex.split(raw[match.start(2):match.end(2)])
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
    """Author timestamp of the user's last commit, or None.

    Author date, not committer date: an --amend or a rebase rewrites the
    commit but keeps its author date, so it does not make HANDOVER.md stale.
    Only commits by the configured user.email count (commits pulled from
    others do not), searched among the last OWN_COMMIT_WINDOW commits. No
    user.email: the last commit, whoever made it.
    """
    email = git(directory, "config", "user.email")
    if not email:
        return git(directory, "log", "-1", "--format=%at")
    log = git(directory, "log", f"-{OWN_COMMIT_WINDOW}", "--format=%ae %at")
    for line in (log or "").splitlines():
        author, _, stamp = line.rpartition(" ")
        if author.lower() == email.lower():
            return stamp
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

    directory = target_dir(raw, command, cwd)
    if not os.path.isdir(directory):
        return

    if env_flag("DEV_WORKFLOW_GUARD_MAIN", True):
        branch, created = branch_after_switch(
            raw,
            command[:COMMIT.search(command).start()],
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
        last_commit = last_own_commit(directory) if handover else None
        if last_commit and os.path.getmtime(handover) < int(last_commit):
            block(
                f"{handover} has not been updated since your last commit: add one "
                "line under 'Since last checkpoint' saying what this commit does "
                "(handover skill), then commit again. To turn this check off, set "
                "DEV_WORKFLOW_GUARD_HANDOVER=0."
            )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
    sys.exit(0)
