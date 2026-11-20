"""Tests for plugins/dev-workflow/hooks/git-guard.py.

Each test builds a throwaway repository, pipes a PreToolUse payload into the
hook and checks the exit code: 2 blocked, 0 allowed.

Run: python3 -m unittest discover -s tests
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

HOOK = os.path.join(
    os.path.dirname(__file__), "..", "plugins", "dev-workflow", "hooks", "git-guard.py"
)
GUARD_VARS = ("DEV_WORKFLOW_GUARD_MAIN", "DEV_WORKFLOW_GUARD_HANDOVER", "DEV_WORKFLOW_BLOCK_PUSH")


def git(repo, *args, email="me@example.com", when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Me", GIT_AUTHOR_EMAIL=email,
               GIT_COMMITTER_NAME="Me", GIT_COMMITTER_EMAIL=email)
    if when is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{int(when)} +0000"
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, env=env)


def make_repo(parent, name="repo", branch="main"):
    repo = os.path.join(parent, name)
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", branch)
    git(repo, "config", "user.email", "me@example.com")
    git(repo, "config", "user.name", "Me")
    git(repo, "commit", "-q", "--allow-empty", "-m", "init")
    return repo


def touch(path, when):
    with open(path, "a", encoding="utf-8"):
        pass
    os.utime(path, (when, when))


class GitGuardTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = os.path.realpath(self._tmp.name)
        self.env = {k: v for k, v in os.environ.items() if k not in GUARD_VARS}

    def tearDown(self):
        self._tmp.cleanup()

    def run_hook(self, command, cwd, **env):
        payload = json.dumps({"cwd": cwd, "tool_input": {"command": command}})
        result = subprocess.run(
            [sys.executable, HOOK], input=payload, capture_output=True, text=True,
            env=dict(self.env, **env),
        )
        return result.returncode

    # Default branch ---------------------------------------------------------

    def test_commit_on_main_blocked(self):
        repo = make_repo(self.tmp)
        self.assertEqual(self.run_hook("git commit -m x", repo), 2)

    def test_commit_on_feature_branch_allowed(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_branch_created_in_same_command_allowed(self):
        repo = make_repo(self.tmp)
        for cmd in ("git switch -c feat/x && git commit -m x",
                    "git checkout -b feat/x main && git commit -m x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.run_hook(cmd, repo), 0)

    def test_switch_to_main_in_same_command_blocked(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        for cmd in ("git switch main && git commit -m x",
                    "git checkout master; git commit -m x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.run_hook(cmd, repo), 2)

    def test_force_create_of_default_branch_blocked(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        for cmd in ("git switch -C main && git commit -m x",
                    "git checkout -B main && git commit -m x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.run_hook(cmd, repo), 2)

    def test_switch_before_or_does_not_count(self):
        repo = make_repo(self.tmp)
        git(repo, "branch", "feat/x")
        self.assertEqual(self.run_hook("git switch feat/x || git commit -m x", repo), 2)

    def test_git_dir_option_with_space(self):
        repo = make_repo(self.tmp)
        self.assertEqual(self.run_hook("git --git-dir .git commit -m x", repo), 2)
        self.assertEqual(self.run_hook("git --no-pager commit -m x", repo), 2)

    def test_checkout_of_a_path_does_not_change_branch(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        self.assertEqual(self.run_hook("git checkout -- main && git commit -m x", repo), 0)

    def test_switch_to_existing_feature_branch_allowed(self):
        repo = make_repo(self.tmp)
        git(repo, "branch", "feat/x")
        self.assertEqual(self.run_hook("git checkout feat/x && git commit -m x", repo), 0)
        self.assertEqual(self.run_hook("git switch feat/x && git commit -m x", repo), 0)

    def test_remote_default_branch_blocked(self):
        repo = make_repo(self.tmp, branch="develop")
        git(repo, "update-ref", "refs/remotes/origin/develop", "HEAD")
        git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/develop")
        self.assertEqual(self.run_hook("git commit -m x", repo), 2)
        other = make_repo(self.tmp, "other", branch="develop")
        self.assertEqual(self.run_hook("git commit -m x", other), 0)

    def test_first_commit_of_new_repo_allowed(self):
        repo = os.path.join(self.tmp, "fresh")
        os.makedirs(repo)
        git(repo, "init", "-q", "-b", "main")
        self.assertEqual(self.run_hook("git commit -m init", repo), 0)

    def test_git_by_path_and_variables_seen(self):
        repo = make_repo(self.tmp)
        feature = make_repo(self.tmp, "feature")
        git(feature, "switch", "-q", "-c", "feat/x")
        self.assertEqual(self.run_hook("/usr/bin/git commit -m x", repo), 2)
        self.assertEqual(self.run_hook('cd "$PWD" && git commit -m x', repo), 2)
        self.assertEqual(self.run_hook(f'cd "$PWD/../{os.path.basename(repo)}" && git commit -m x', feature), 2)

    def test_marker_allows_main(self):
        repo = make_repo(self.tmp)
        os.makedirs(os.path.join(repo, ".claude"))
        touch(os.path.join(repo, ".claude", "allow-main-commits"), time.time())
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_env_turns_main_check_off(self):
        repo = make_repo(self.tmp)
        self.assertEqual(self.run_hook("git commit -m x", repo, DEV_WORKFLOW_GUARD_MAIN="0"), 0)

    def test_git_dash_c_and_cd_target_other_repo(self):
        feature = make_repo(self.tmp, "feature")
        git(feature, "switch", "-q", "-c", "feat/x")
        main = make_repo(self.tmp, "main-repo")
        self.assertEqual(self.run_hook(f"git -C {main} commit -m x", feature), 2)
        self.assertEqual(self.run_hook(f"cd {main} && git commit -m x", feature), 2)

    def test_quoted_branch_name_switch_blocked(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        self.assertEqual(self.run_hook('git switch "main" && git commit -m x', repo), 2)

    def test_git_dash_c_with_spaces_in_path(self):
        os.makedirs(os.path.join(self.tmp, "with space"))
        main = make_repo(os.path.join(self.tmp, "with space"))
        feature = make_repo(self.tmp, "feature")
        git(feature, "switch", "-q", "-c", "feat/x")
        self.assertEqual(self.run_hook(f'git -C "{main}" commit -m x', feature), 2)
        self.assertEqual(self.run_hook(f'cd "{main}" && git commit -m x', feature), 2)

    def test_cd_inside_quoted_string_ignored(self):
        main = make_repo(self.tmp, "main-repo")
        feature = make_repo(self.tmp, "feature")
        git(feature, "switch", "-q", "-c", "feat/x")
        cmd = f'echo "done; cd {main}" && git commit -m x'
        self.assertEqual(self.run_hook(cmd, feature), 0)

    # Text that is data, not commands ------------------------------------------

    def test_quoted_and_heredoc_text_ignored(self):
        repo = make_repo(self.tmp)
        git(repo, "switch", "-q", "-c", "feat/x")
        cmds = (
            'git commit -m "then run git switch main && git commit"',
            "git commit -F - <<'EOF'\ngit switch main\nEOF",
        )
        for cmd in cmds:
            with self.subTest(cmd=cmd):
                self.assertEqual(self.run_hook(cmd, repo), 0)

    def test_non_commit_commands_ignored(self):
        repo = make_repo(self.tmp)
        for cmd in ("git status", "git log -1", 'echo "git commit"', "ls",
                    "git status # then git commit", "# git commit\nls",
                    "git commit-tree HEAD^{tree} -m x", "git commit-graph write"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.run_hook(cmd, repo), 0)

    # HANDOVER.md ----------------------------------------------------------------

    def feature_repo(self, name="repo", when=None, ignore=True):
        repo = make_repo(self.tmp, name)
        git(repo, "switch", "-q", "-c", "feat/x")
        if ignore:
            with open(os.path.join(repo, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
                f.write("HANDOVER.md\n")
        if when is not None:
            git(repo, "commit", "-q", "--allow-empty", "-m", "work", when=when)
        return repo

    def test_stale_handover_blocked(self):
        now = time.time()
        repo = self.feature_repo(when=now)
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        self.assertEqual(self.run_hook("git commit -m x", repo), 2)
        self.assertEqual(
            self.run_hook("git commit -m x", repo, DEV_WORKFLOW_GUARD_HANDOVER="0"), 0
        )

    def test_fresh_handover_allowed(self):
        now = time.time()
        repo = self.feature_repo(when=now - 3600)
        touch(os.path.join(repo, "HANDOVER.md"), now)
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_no_handover_no_check(self):
        repo = self.feature_repo(when=time.time())
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_commits_by_others_do_not_count(self):
        now = time.time()
        repo = self.feature_repo(when=now - 7200)
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        git(repo, "commit", "-q", "--allow-empty", "-m", "pulled", email="other@example.com", when=now)
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_amend_does_not_make_handover_stale(self):
        now = time.time()
        repo = self.feature_repo(when=now - 7200)
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        # amend: committer date moves to now, author date stays 2 h ago
        env = dict(os.environ, GIT_COMMITTER_DATE=f"@{int(now)} +0000")
        subprocess.run(["git", "-C", repo, "commit", "-q", "--amend", "--allow-empty", "-m", "w2"],
                       check=True, capture_output=True, env=env)
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_handover_not_ignored_blocked(self):
        now = time.time()
        repo = self.feature_repo(when=now - 3600, ignore=False)
        touch(os.path.join(repo, "HANDOVER.md"), now)
        self.assertEqual(self.run_hook("git add -A && git commit -m x", repo), 2)

    def test_staged_handover_blocked_even_if_fresh(self):
        now = time.time()
        repo = self.feature_repo(when=now - 3600)
        touch(os.path.join(repo, "HANDOVER.md"), now)
        git(repo, "add", "-f", "HANDOVER.md")
        self.assertEqual(self.run_hook("git commit -m x", repo), 2)

    def test_amend_not_checked(self):
        now = time.time()
        repo = self.feature_repo(when=now)
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        self.assertEqual(self.run_hook("git commit --amend --no-edit", repo), 0)
        self.assertEqual(self.run_hook("git commit -m x", repo), 2)

    def test_tracked_handover_not_checked(self):
        now = time.time()
        repo = self.feature_repo()
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        git(repo, "add", "-f", "HANDOVER.md")
        git(repo, "commit", "-q", "-m", "team handover", when=now)
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_no_own_commit_no_check(self):
        now = time.time()
        repo = self.feature_repo()
        git(repo, "commit", "-q", "--amend", "--reset-author", "--allow-empty", "-m", "init",
            email="other@example.com", when=now)
        touch(os.path.join(repo, "HANDOVER.md"), now - 3600)
        self.assertEqual(self.run_hook("git commit -m x", repo), 0)

    def test_session_handover_ignored_for_other_repo(self):
        now = time.time()
        session = self.feature_repo("session", when=now - 7200)
        touch(os.path.join(session, "HANDOVER.md"), now - 3600)
        other = self.feature_repo("other", when=now)
        self.assertEqual(self.run_hook(f"git -C {other} commit -m x", session), 0)
        self.assertEqual(self.run_hook(f"cd {other} && git commit -m x", session), 0)

    # Push and robustness --------------------------------------------------------

    def test_push_allowed_by_default_blocked_on_demand(self):
        repo = make_repo(self.tmp)
        self.assertEqual(self.run_hook("git push", repo), 0)
        self.assertEqual(self.run_hook("git push", repo, DEV_WORKFLOW_BLOCK_PUSH="1"), 2)

    def test_bad_input_allowed(self):
        for payload in ("", "not json", "[]", '{"tool_input": {}}'):
            with self.subTest(payload=payload):
                result = subprocess.run(
                    [sys.executable, HOOK], input=payload, capture_output=True, text=True,
                    env=self.env,
                )
                self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
