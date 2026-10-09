import hashlib
import io
import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "install_engram.py"
FAKE = """#!/usr/bin/env python3
import os, pathlib, sys
with pathlib.Path(os.environ["FAKE_LOG"]).open("a") as f:
    f.write(pathlib.Path(sys.argv[0]).name + " " + " ".join(sys.argv[1:]) + "\\n")
"""


def make_release(root, version="9.9.9", os_name="linux", arch="amd64",
                 corrupt=False):
    release = pathlib.Path(root) / "release"
    release.mkdir()
    asset = f"engram_{version}_{os_name}_{arch}.tar.gz"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        data = b"#!/bin/sh\necho engram\n"
        info = tarfile.TarInfo("engram")
        info.size = len(data)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(data))
    blob = buf.getvalue()
    (release / asset).write_bytes(blob)
    digest = hashlib.sha256(b"other" if corrupt else blob).hexdigest()
    (release / "checksums.txt").write_text(f"{digest}  {asset}\n")
    return release


def fake_tool(root, name):
    path = pathlib.Path(root) / "tools" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(FAKE)
    path.chmod(0o755)
    return path


def run(root, *args, release=None, path_extra=None, **env):
    bin_dir = pathlib.Path(root) / "bin"
    base = {"PATH": "/usr/bin:/bin", "HOME": str(root),
            "FAKE_LOG": str(pathlib.Path(root) / "calls.log"),
            "CLAUDE_BIN": str(fake_tool(root, "claude"))}
    if path_extra:
        base["PATH"] = path_extra + ":" + base["PATH"]
    base.update(env)
    cmd = [sys.executable, str(SCRIPT), "--version", "9.9.9",
           "--bin-dir", str(bin_dir)]
    if release:
        cmd += ["--base-url", release.as_uri()]
    done = subprocess.run(cmd + list(args), capture_output=True, text=True,
                          env=base)
    log = pathlib.Path(root) / "calls.log"
    calls = log.read_text().splitlines() if log.exists() else []
    return done, calls, bin_dir


class Binary(unittest.TestCase):
    def test_it_installs_the_downloaded_binary(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root)
            done, _, bin_dir = run(root, release=release,
                                   OS_NAME="linux", ARCH="x86_64")
            self.assertEqual(done.returncode, 0, done.stderr)
            engram = bin_dir / "engram"
            self.assertTrue(engram.exists())
            self.assertTrue(os.access(engram, os.X_OK))

    def test_a_bad_checksum_installs_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root, corrupt=True)
            done, _, bin_dir = run(root, release=release,
                                   OS_NAME="linux", ARCH="x86_64")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("checksum", done.stderr)
            self.assertFalse((bin_dir / "engram").exists())

    def test_the_asset_name_follows_the_platform(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root, os_name="darwin", arch="arm64")
            done, _, bin_dir = run(root, release=release,
                                   OS_NAME="darwin", ARCH="arm64")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertTrue((bin_dir / "engram").exists())

    def test_windows_is_not_supported(self):
        with tempfile.TemporaryDirectory() as root:
            done, _, _ = run(root, release=make_release(root),
                             OS_NAME="windows", ARCH="x86_64")
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("INSTALLATION.md", done.stderr)

    def test_an_installed_engram_is_left_alone(self):
        with tempfile.TemporaryDirectory() as root:
            fake_tool(root, "engram")
            release = make_release(root, corrupt=True)
            done, _, bin_dir = run(root, release=release,
                                   path_extra=str(pathlib.Path(root) / "tools"),
                                   OS_NAME="linux", ARCH="x86_64")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertFalse((bin_dir / "engram").exists())


class Plugin(unittest.TestCase):
    def test_the_plugin_is_installed_at_local_scope(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root)
            done, calls, _ = run(root, release=release,
                                 OS_NAME="linux", ARCH="x86_64")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn(
                "claude plugin marketplace add Gentleman-Programming/engram",
                calls)
            self.assertIn("claude plugin install engram --scope local", calls)

    def test_the_mcp_server_is_registered_at_local_scope(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root)
            done, calls, bin_dir = run(root, release=release,
                                       OS_NAME="linux", ARCH="x86_64")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn(
                f"claude mcp add --transport stdio --scope local engram -- "
                f"{bin_dir / 'engram'} mcp --tools=agent", calls)

    def test_setup_runs_only_with_the_user_flag(self):
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root)
            _, calls, _ = run(root, release=release,
                              OS_NAME="linux", ARCH="x86_64")
            self.assertFalse(any("setup" in c for c in calls))
        with tempfile.TemporaryDirectory() as root:
            release = make_release(root)
            fake_tool(root, "engram")
            _, calls, _ = run(root, "--user", release=release,
                              path_extra=str(pathlib.Path(root) / "tools"),
                              OS_NAME="linux", ARCH="x86_64")
            self.assertIn("engram setup claude-code", calls)


if __name__ == "__main__":
    unittest.main()
