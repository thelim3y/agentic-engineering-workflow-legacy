import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "setup_scratch.py"
FAKE_GH = """#!/usr/bin/env python3
import os, pathlib, sys
log = pathlib.Path(os.environ["FAKE_GH_LOG"])
count = log.parent / "count"
with log.open("a") as f:
    f.write(" ".join(a.replace("\\n", " / ") for a in sys.argv[1:]) + "\\n")
if sys.argv[1:3] == ["issue", "create"]:
    n = int(count.read_text()) + 1 if count.exists() else 1
    count.write_text(str(n))
    print(f"https://github.com/o/r/issues/{n}")
"""


def setup(target, *args, env=None):
    base = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    base.update(env or {})
    return subprocess.run([sys.executable, str(SCRIPT), str(target), *args],
                          capture_output=True, text=True, env=base)


class Local(unittest.TestCase):
    def test_it_creates_a_project_whose_tests_pass(self):
        with tempfile.TemporaryDirectory() as root:
            target = pathlib.Path(root) / "scratch"
            done = setup(target)
            self.assertEqual(done.returncode, 0, done.stderr)
            tests = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                cwd=target, capture_output=True, text=True)
            self.assertEqual(tests.returncode, 0, tests.stderr)

    def test_it_writes_the_files_the_workflow_needs(self):
        with tempfile.TemporaryDirectory() as root:
            target = pathlib.Path(root) / "scratch"
            setup(target)
            toml = (target / "agentic.toml").read_text()
            self.assertIn('tests = ["tests/**"]', toml)
            self.assertIn(".agentic/", (target / ".gitignore").read_text())
            self.assertIn("unittest", (target / "CLAUDE.md").read_text())

    def test_it_makes_a_git_repository_with_one_commit(self):
        with tempfile.TemporaryDirectory() as root:
            target = pathlib.Path(root) / "scratch"
            setup(target)
            count = subprocess.run(
                ["git", "-C", str(target), "rev-list", "--count", "HEAD"],
                capture_output=True, text=True).stdout.strip()
            self.assertEqual(count, "1")

    def test_it_refuses_a_folder_that_is_not_empty(self):
        with tempfile.TemporaryDirectory() as root:
            (pathlib.Path(root) / "x").write_text("x")
            done = setup(root)
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("not empty", done.stderr)

    def test_it_uses_no_github_without_the_flag(self):
        with tempfile.TemporaryDirectory() as root:
            log = pathlib.Path(root) / "gh.log"
            fake = pathlib.Path(root) / "gh"
            fake.write_text(FAKE_GH)
            fake.chmod(0o755)
            setup(pathlib.Path(root) / "scratch",
                  env={"GH_BIN": str(fake), "FAKE_GH_LOG": str(log)})
            self.assertFalse(log.exists())


class GitHub(unittest.TestCase):
    def run_github(self):
        root = tempfile.mkdtemp()
        log = pathlib.Path(root) / "gh.log"
        fake = pathlib.Path(root) / "gh"
        fake.write_text(FAKE_GH)
        fake.chmod(0o755)
        done = setup(pathlib.Path(root) / "scratch", "--github", "o/r",
                     env={"GH_BIN": str(fake), "FAKE_GH_LOG": str(log)})
        self.assertEqual(done.returncode, 0, done.stderr)
        return log.read_text().splitlines()

    def test_it_creates_a_private_repository(self):
        calls = self.run_github()
        create = [c for c in calls if c.startswith("repo create")][0]
        self.assertIn("o/r", create)
        self.assertIn("--private", create)

    def test_it_creates_the_three_labels(self):
        calls = self.run_github()
        for label in ("ai-ready", "epic", "parent-issue"):
            self.assertTrue(
                any(c.startswith("label create " + label) for c in calls),
                label)

    def test_it_creates_an_epic_and_two_ready_issues(self):
        calls = self.run_github()
        issues = [c for c in calls if c.startswith("issue create")]
        self.assertEqual(len(issues), 3)
        self.assertIn("--label epic", issues[0])
        self.assertTrue(all("--label ai-ready" in c for c in issues[1:]))

    def test_the_epic_lists_its_children_in_order(self):
        calls = self.run_github()
        edit = [c for c in calls if c.startswith("issue edit 1")][0]
        self.assertIn("#2, #3, in that order", edit)


if __name__ == "__main__":
    unittest.main()
