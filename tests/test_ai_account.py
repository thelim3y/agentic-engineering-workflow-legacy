import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "ai_account.py"
FAKE_GH = """#!/usr/bin/env python3
import os, pathlib, sys
a = sys.argv[1:]
with pathlib.Path(os.environ["FAKE_LOG"]).open("a") as f:
    f.write("gh " + " ".join(a) + " TOKEN=" + os.environ.get("GH_TOKEN", "") + "\\n")
if a[:2] == ["api", "user"]:
    print('{"login": "%s"}' % os.environ.get("FAKE_LOGIN", "ai-bot"))
elif a[:1] == ["api"] and "collaborators" in " ".join(a):
    print("{}")
elif a[:1] == ["api"]:
    print('{"permissions": {"push": %s}}' % os.environ.get("FAKE_PUSH", "true"))
"""
FAKE_SSH = """#!/usr/bin/env python3
import os
print(os.environ.get("FAKE_SSH_SAYS", "Hi ai-bot! You've successfully authenticated, but GitHub does not provide shell access."))
raise SystemExit(1)
"""
FAKE_KEYGEN = """#!/usr/bin/env python3
import pathlib, sys
a = sys.argv[1:]
key = pathlib.Path(a[a.index("-f") + 1])
key.write_text("PRIVATE")
pathlib.Path(str(key) + ".pub").write_text("ssh-ed25519 AAAA ai-bot")
"""


def tool(root, name, body):
    path = pathlib.Path(root) / "tools" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)
    return str(path)


def run(root, *args, **env):
    base = {"PATH": os.environ["PATH"], "HOME": str(root),
            "FAKE_LOG": str(pathlib.Path(root) / "calls.log"),
            "GH_BIN": tool(root, "gh", FAKE_GH),
            "SSH_BIN": tool(root, "ssh", FAKE_SSH),
            "SSH_KEYGEN_BIN": tool(root, "ssh-keygen", FAKE_KEYGEN)}
    base.update(env)
    done = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, env=base,
                          cwd=str(root))
    log = pathlib.Path(root) / "calls.log"
    return done, (log.read_text().splitlines() if log.exists() else [])


def init(root, *extra, **env):
    return run(root, "init", "--account", "ai-bot", "--repo", "o/r",
               "--key", str(pathlib.Path(root) / "ai_key"), *extra, **env)


class Init(unittest.TestCase):
    def test_it_makes_a_key_when_there_is_none(self):
        with tempfile.TemporaryDirectory() as root:
            done, _ = init(root)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertTrue((pathlib.Path(root) / "ai_key").exists())
            self.assertIn("ssh-ed25519 AAAA", done.stdout)

    def test_it_keeps_an_existing_key(self):
        with tempfile.TemporaryDirectory() as root:
            key = pathlib.Path(root) / "ai_key"
            key.write_text("MINE")
            (pathlib.Path(root) / "ai_key.pub").write_text("ssh-ed25519 MINE")
            init(root)
            self.assertEqual(key.read_text(), "MINE")

    def test_it_writes_the_github_section(self):
        with tempfile.TemporaryDirectory() as root:
            (pathlib.Path(root) / "agentic.toml").write_text(
                '[limits]\\nattempts_per_step = 3\\n')
            init(root, "--author-name", "AI Bot", "--author-email", "a@b.c")
            toml = (pathlib.Path(root) / "agentic.toml").read_text()
            self.assertIn("attempts_per_step = 3", toml)
            self.assertIn("[github]", toml)
            self.assertIn('ai_account = "ai-bot"', toml)
            self.assertIn('commit_author_name = "AI Bot"', toml)
            self.assertIn('token_env_var = "AGENTIC_GH_TOKEN"', toml)

    def test_running_it_again_does_not_duplicate_the_section(self):
        with tempfile.TemporaryDirectory() as root:
            init(root)
            init(root)
            toml = (pathlib.Path(root) / "agentic.toml").read_text()
            self.assertEqual(toml.count("[github]"), 1)

    def test_it_invites_the_account_with_write_access(self):
        with tempfile.TemporaryDirectory() as root:
            _, calls = init(root)
            self.assertTrue(any("collaborators/ai-bot" in c and "push" in c
                                for c in calls), calls)

    def test_it_lists_what_is_left_to_do_by_hand(self):
        with tempfile.TemporaryDirectory() as root:
            done, _ = init(root)
            for text in ("settings/ssh/new", "personal-access-tokens/new",
                         "invitations", "AGENTIC_GH_TOKEN"):
                self.assertIn(text, done.stdout)


class Check(unittest.TestCase):
    def ready(self, root):
        init(root)
        return run(root, "check", AGENTIC_GH_TOKEN="tok")

    def test_everything_in_place_passes(self):
        with tempfile.TemporaryDirectory() as root:
            done, calls = self.ready(root)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertNotIn("✗", done.stdout)
            self.assertTrue(any("TOKEN=tok" in c for c in calls))

    def test_a_missing_token_is_reported_with_the_fix(self):
        with tempfile.TemporaryDirectory() as root:
            init(root)
            done, _ = run(root, "check")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("✗", done.stdout)
            self.assertIn("export AGENTIC_GH_TOKEN", done.stdout)

    def test_a_token_for_the_wrong_account_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            init(root)
            done, _ = run(root, "check", AGENTIC_GH_TOKEN="tok",
                          FAKE_LOGIN="someone-else")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("someone-else", done.stdout)

    def test_a_key_that_is_not_accepted_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            init(root)
            done, _ = run(root, "check", AGENTIC_GH_TOKEN="tok",
                          FAKE_SSH_SAYS="Permission denied (publickey).")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("settings/ssh/new", done.stdout)

    def test_no_write_access_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            init(root)
            done, _ = run(root, "check", AGENTIC_GH_TOKEN="tok",
                          FAKE_PUSH="false")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("invitations", done.stdout)


if __name__ == "__main__":
    unittest.main()
