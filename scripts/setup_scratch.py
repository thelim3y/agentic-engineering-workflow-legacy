#!/usr/bin/env python3
"""Create a small scratch project to try the workflow on.

    python3 scripts/setup_scratch.py <folder> [--github OWNER/NAME]

Without --github nothing leaves the machine. With it, a private GitHub
repository is created, with the labels and three issues to run the workflow on.
"""

import argparse
import os
import pathlib
import re
import subprocess
import sys

FILES = {
    "agentic.toml": '[limits]\nmax_files = 3\n\n[paths]\ntests = ["tests/**"]\n',
    ".gitignore": ".agentic/\n__pycache__/\n",
    "README.md": "# Scratch project\n\nA tiny project for trying the "
                 "agentic-engineering-workflow plugin.\n",
    "CLAUDE.md": "# Scratch project\n\nRun the tests with "
                 "`python3 -m unittest discover -s tests`.\n",
    "calc/__init__.py": "",
    "calc/ops.py": "def multiply(a, b):\n    return a * b\n",
    "tests/__init__.py": "",
    "tests/test_ops.py": (
        "import unittest\n\nfrom calc.ops import multiply\n\n\n"
        "class Multiply(unittest.TestCase):\n"
        "    def test_it_multiplies_two_numbers(self):\n"
        "        self.assertEqual(multiply(3, 4), 12)\n\n\n"
        'if __name__ == "__main__":\n    unittest.main()\n'),
}

SMALL = ("Add an add function",
         "Add `add(a, b)` to `calc/ops.py`. It returns the sum of its two "
         "arguments.")
LARGE = ("Add a statistics module",
         "Add a `calc/stats.py` with `mean`, `median`, `mode`, `variance` and "
         "`standard_deviation`, each tested, and a command line that prints "
         "all five for numbers given as arguments.")


def run(*args, **kw):
    return subprocess.run(args, check=True, text=True, **kw)


def create_project(target):
    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()):
        sys.exit(f"{target} is not empty")
    for name, text in FILES.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    run("git", "-C", str(target), "init", "-q")
    run("git", "-C", str(target), "add", "-A")
    run("git", "-C", str(target), "commit", "-q", "-m", "Scratch project")


def issue_number(gh, repo, title, body, label):
    out = run(gh, "issue", "create", "--repo", repo, "--title", title,
              "--body", body, "--label", label, capture_output=True).stdout
    return int(re.search(r"/issues/(\d+)", out).group(1))


def create_github(target, repo):
    gh = os.environ.get("GH_BIN", "gh")
    run(gh, "repo", "create", repo, "--private", "--source", str(target),
        "--push")
    for label in ("ai-ready", "epic", "parent-issue"):
        run(gh, "label", "create", label, "--repo", repo, "--force")
    epic = issue_number(gh, repo, "Scratch epic",
                        "Tickets for trying the workflow.", "epic")
    small = issue_number(gh, repo, SMALL[0],
                         f"Parent epic: #{epic}\n\n{SMALL[1]}", "ai-ready")
    large = issue_number(gh, repo, LARGE[0],
                         f"Parent epic: #{epic}\n\n{LARGE[1]}", "ai-ready")
    run(gh, "issue", "edit", str(epic), "--repo", repo, "--body",
        f"Tickets for trying the workflow.\n\n#{small}, #{large}, "
        "in that order")
    print(f"Epic #{epic}; small issue #{small}; large issue #{large}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=pathlib.Path)
    parser.add_argument("--github", metavar="OWNER/NAME")
    args = parser.parse_args()
    create_project(args.folder)
    if args.github:
        create_github(args.folder, args.github)
    print(f"Scratch project ready in {args.folder}")


if __name__ == "__main__":
    main()
