#!/usr/bin/env python3
"""PreToolUse hook: enforce each agent's file and command limits.

Reads the hook event on stdin. A call from the main session, or from an agent
with no rule here, passes. A call that breaks a rule is denied with a reason.
"""

import json
import pathlib
import re
import shlex
import sys
import tomllib

READ_ONLY_GH_PR = ("view", "diff", "checks", "list", "status")

# Agent -> (allowed command prefixes, or None), (denied command prefixes)
COMMAND_RULES = {
    "task-scoper": {"allow": [("gh", "issue"), ("gh", "api")]},
    "tdd-maestro": {"deny": [("git", "push"), ("gh",)]},
    "code-fu": {"deny": [("git", "push"), ("gh",)]},
    "test-runner": {"deny": [("git",), ("gh",)]},
    "pr-evaluator": {"allow": [("git", "status"), ("git", "diff"),
                               ("git", "log")]},
    "committer": {"allow": [("git", "status"), ("git", "diff"),
                            ("git", "add"), ("git", "commit")]},
    "pr-create": {"allow": [("git", "status"), ("git", "log"),
                            ("git", "push"), ("gh", "pr", "create")]},
    "pr-reviewer": {"allow": [("git", "diff"), ("git", "log")]
                    + [("gh", "pr", v) for v in READ_ONLY_GH_PR]},
    "merge-evaluator": {"allow": [("gh", "pr", v) for v in READ_ONLY_GH_PR]},
    "merger-mage": {"allow": [("gh", "pr", "view"), ("gh", "pr", "merge"),
                              ("gh", "issue", "close"), ("gh", "api")]},
}


def agent_name(event):
    name = event.get("agent_type") or ""
    return name.split(":")[-1]


def deny(agent, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"{agent}: {reason}"}}))


def glob_regex(pattern):
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r"\Z")


def test_globs(cwd):
    try:
        with open(pathlib.Path(cwd) / "agentic.toml", "rb") as f:
            return tomllib.load(f).get("paths", {}).get("tests") or []
    except (OSError, tomllib.TOMLDecodeError):
        return []


def relative(path, cwd):
    p = pathlib.Path(path)
    try:
        return p.relative_to(cwd).as_posix() if p.is_absolute() else p.as_posix()
    except ValueError:
        return p.as_posix()


def check_file(agent, event):
    if agent not in ("tdd-maestro", "code-fu"):
        return
    cwd = event.get("cwd", ".")
    globs = test_globs(cwd)
    if not globs:
        return deny(agent, "paths.tests is not set in agentic.toml, so no "
                    "edit is allowed until it is.")
    path = relative(event["tool_input"].get("file_path", ""), cwd)
    is_test = any(glob_regex(g).match(path) for g in globs)
    if agent == "tdd-maestro" and not is_test:
        return deny(agent, f"{path} is not a test file (paths.tests); "
                    "tdd-maestro edits only test files.")
    if agent == "code-fu" and is_test:
        return deny(agent, f"{path} is a test file (paths.tests); code-fu "
                    "edits no test. Return TEST_DISPUTED instead.")


def segments(command):
    parts = re.split(r"&&|\|\||;|\||\n", command)
    for part in parts:
        try:
            words = shlex.split(part)
        except ValueError:
            words = part.split()
        while words and re.match(r"[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            words = words[1:]
        if words:
            yield words


def starts_with(words, prefix):
    return tuple(words[:len(prefix)]) == prefix


def check_command(agent, event):
    rules = COMMAND_RULES.get(agent)
    if not rules:
        return
    for words in segments(event["tool_input"].get("command", "")):
        if any(starts_with(words, p) for p in rules.get("deny", [])):
            return deny(agent, f"`{' '.join(words[:3])}` is not allowed "
                        "for this agent.")
        allow = rules.get("allow")
        if allow is not None and not any(starts_with(words, p) for p in allow):
            return deny(agent, f"`{' '.join(words[:3])}` is not on this "
                        "agent's list of allowed commands.")


def main():
    event = json.load(sys.stdin)
    agent = agent_name(event)
    if not agent:
        return
    tool = event.get("tool_name")
    if tool in ("Edit", "Write"):
        check_file(agent, event)
    elif tool == "Bash":
        check_command(agent, event)


if __name__ == "__main__":
    main()
