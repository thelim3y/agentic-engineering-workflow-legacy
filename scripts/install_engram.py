#!/usr/bin/env python3
"""Install engram and its Claude Code plugin for the current project.

    python3 scripts/install_engram.py [--user]

1. The engram binary: Homebrew if present, otherwise the release file for this
   machine, checked against the release's checksums and put in ~/.local/bin.
2. The engram plugin, at local scope: this project and this user only.

--user also runs `engram setup claude-code`, which registers engram for every
Claude Code session of the user.
"""

import argparse
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

REPO = "Gentleman-Programming/engram"
BASE = f"https://github.com/{REPO}/releases/download"
ARCHES = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64",
          "arm64": "arm64"}


def fail(message):
    sys.exit(f"install_engram: {message}")


def platform_names():
    os_name = os.environ.get("OS_NAME") or platform.system().lower()
    arch = os.environ.get("ARCH") or platform.machine().lower()
    if os_name not in ("linux", "darwin") or arch not in ARCHES:
        fail(f"no release file for {os_name}/{arch}; see engram's "
             "docs/INSTALLATION.md")
    return os_name, ARCHES[arch]


def latest_version():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    with urllib.request.urlopen(url) as response:
        return json.load(response)["tag_name"].lstrip("v")


def fetch(url):
    with urllib.request.urlopen(url) as response:
        return response.read()


def install_binary(version, base_url, bin_dir):
    os_name, arch = platform_names()
    asset = f"engram_{version}_{os_name}_{arch}.tar.gz"
    root = base_url or f"{BASE}/v{version}"
    blob = fetch(f"{root}/{asset}")
    sums = fetch(f"{root}/checksums.txt").decode()
    expected = next((line.split()[0] for line in sums.splitlines()
                     if line.split()[-1:] == [asset]), None)
    if expected != hashlib.sha256(blob).hexdigest():
        fail(f"checksum of {asset} does not match checksums.txt")
    with tempfile.TemporaryDirectory() as tmp:
        archive = pathlib.Path(tmp) / asset
        archive.write_bytes(blob)
        with tarfile.open(archive) as tar:
            member = next(m for m in tar.getmembers()
                          if pathlib.Path(m.name).name == "engram")
            data = tar.extractfile(member).read()
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "engram"
    target.write_bytes(data)
    target.chmod(0o755)
    print(f"Installed {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--version")
    parser.add_argument("--bin-dir", type=pathlib.Path,
                        default=pathlib.Path.home() / ".local" / "bin")
    parser.add_argument("--base-url")
    parser.add_argument("--user", action="store_true")
    args = parser.parse_args()

    claude = os.environ.get("CLAUDE_BIN", "claude")
    if shutil.which("engram"):
        print("engram is already installed")
    elif shutil.which("brew"):
        subprocess.run(["brew", "install", "gentleman-programming/tap/engram"],
                       check=True)
    else:
        install_binary(args.version or latest_version(), args.base_url,
                       args.bin_dir)

    subprocess.run([claude, "plugin", "marketplace", "add", REPO], check=True)
    subprocess.run([claude, "plugin", "install", "engram", "--scope", "local"],
                   check=True)
    if args.user:
        engram = shutil.which("engram") or str(args.bin_dir / "engram")
        subprocess.run([engram, "setup", "claude-code"], check=True)


if __name__ == "__main__":
    main()
