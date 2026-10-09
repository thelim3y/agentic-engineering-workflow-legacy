#!/usr/bin/env python3
"""PreToolUse hook: enforce each agent's file and command limits.

Reads the hook event on stdin. A call from the main session, or from an agent
with no rule here, passes. A call that breaks a rule is denied with a reason.
"""

import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import tomllib

READ_ONLY_GH_PR = ("view", "diff", "checks", "list", "status")

# Agent -> (allowed command prefixes, or None), (denied command prefixes)
COMMAND_RULES = {
    "task-scoper": {"allow": [("gh", "issue"), ("gh", "api"),
                              ("gh", "repo", "view")]},
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


MEM_SAVE = ("mcp__engram__mem_save", "mcp__plugin_engram_engram__mem_save")
AGENTS = set(COMMAND_RULES) | {"task-planner"}
READ_ONLY_COMMANDS = {"ls", "cat", "head", "tail", "wc", "pwd", "grep", "rg",
                      "find", "stat", "diff", "sort", "uniq", "tree", "file",
                      "cd", "echo", "printf", "true", "test", "["}
READ_ONLY_GIT = [("git", "ls-files"), ("git", "rev-parse"), ("git", "status"),
                 ("git", "log"), ("git", "diff"), ("git", "show")]
CONTROL_PREFIXES = {"do", "then", "else", "if", "elif", "while", "until"}
CONTROL_ONLY = {"for", "done", "fi"}


def agent_name(event):
    name = event.get("agent_type") or ""
    return name.split(":")[-1]


def deny(agent, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"{agent}: {reason}"}}))
    sys.exit(0)


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


def config_dirs(cwd):
    """The directory itself, then the main checkout when it is a worktree."""
    yield pathlib.Path(cwd)
    try:
        common = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--path-format=absolute",
             "--git-common-dir"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return
    yield pathlib.Path(common).parent


def load_config(cwd):
    for directory in config_dirs(cwd):
        try:
            with open(directory / "agentic.toml", "rb") as f:
                return tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            continue
    return {}


def test_globs(cwd):
    return load_config(cwd).get("paths", {}).get("tests") or []


def project_root(cwd):
    try:
        return pathlib.Path(subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return pathlib.Path(cwd)


def dry_run(cwd):
    runs = load_config(cwd).get("paths", {}).get("runs", ".agentic")
    return any((project_root(cwd) / runs).glob("*/dry-run"))


READ_ONLY_GH = {("issue", "view"), ("issue", "list"), ("issue", "status"),
                ("pr", "view"), ("pr", "diff"), ("pr", "checks"),
                ("pr", "list"), ("pr", "status"), ("repo", "view")}
API_WRITES = {"-X", "--method", "-f", "-F", "--field", "--raw-field",
              "--input"}


def remote_effect(words):
    """True when the command changes something outside the machine."""
    if starts_with(words, ("git", "push")):
        return True
    if words[0] != "gh":
        return False
    if len(words) > 1 and words[1] == "api":
        for i, word in enumerate(words[2:], 2):
            if word in API_WRITES and not (
                    word in ("-X", "--method")
                    and words[i + 1:i + 2] == ["GET"]):
                return True
        return False
    return tuple(words[1:3]) not in READ_ONLY_GH


def relative(path, root):
    p = pathlib.Path(path)
    try:
        return p.relative_to(root).as_posix() if p.is_absolute() else p.as_posix()
    except ValueError:
        return p.as_posix()


def check_file(agent, event):
    if agent not in AGENTS:
        return
    cwd = event.get("cwd", ".")
    root = project_root(cwd)
    path = relative(event["tool_input"].get("file_path", ""), root)
    runs = load_config(cwd).get("paths", {}).get("runs", ".agentic")
    if path == runs or path.startswith(runs.rstrip("/") + "/"):
        return
    if agent not in ("tdd-maestro", "code-fu"):
        return deny(agent, f"{path} is outside the run folder ({runs}); "
                    "this agent writes only its report there.")
    globs = test_globs(cwd)
    if not globs:
        return deny(agent, "paths.tests is not set in agentic.toml, so no "
                    "edit is allowed until it is.")
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
        while words and words[0] in CONTROL_PREFIXES:
            words = words[1:]
        if words and words[0] not in CONTROL_ONLY:
            yield words


def starts_with(words, prefix):
    return tuple(words[:len(prefix)]) == prefix


def read_only(words):
    if any(starts_with(words, p) for p in READ_ONLY_GIT):
        return True
    if words[0] not in READ_ONLY_COMMANDS:
        return False
    return not (words[0] == "find" and any(
        w in ("-delete", "-exec", "-execdir", "-ok", "-okdir") for w in words))


def check_command(agent, event):
    rules = COMMAND_RULES.get(agent)
    if not rules:
        return
    for words in segments(event["tool_input"].get("command", "")):
        if any(starts_with(words, p) for p in rules.get("deny", [])):
            return deny(agent, f"`{' '.join(words[:3])}` is not allowed "
                        "for this agent.")
        allow = rules.get("allow")
        if allow is not None and not (
                any(starts_with(words, p) for p in allow)
                or read_only(words)):
            return deny(agent, f"`{' '.join(words[:3])}` is not on this "
                        "agent's list of allowed commands.")


def check_dry_run(event):
    tool = event.get("tool_name")
    if tool in MEM_SAVE:
        return deny("dry run", "memory is not written in a dry run.")
    if tool != "Bash":
        return
    for words in segments(event["tool_input"].get("command", "")):
        if remote_effect(words):
            return deny("dry run", f"`{' '.join(words[:3])}` changes "
                        "something outside this machine, which a dry run "
                        "never does.")


def run_as_account(agent, event):
    """Rewrite an agent's command to run as the configured GitHub account."""
    github = load_config(event.get("cwd", ".")).get("github")
    if not github:
        return
    exports = []
    token_env = github.get("token_env")
    if token_env:
        if not os.environ.get(token_env):
            return deny(agent, f"${token_env} is not set, so this command "
                        "would run as you and not as the AI account.")
        exports.append(f'GH_TOKEN="${token_env}"')
    name, email = github.get("author_name"), github.get("author_email")
    if name:
        exports += [f"GIT_AUTHOR_NAME={shlex.quote(name)}",
                    f"GIT_COMMITTER_NAME={shlex.quote(name)}"]
    if email:
        exports += [f"GIT_AUTHOR_EMAIL={shlex.quote(email)}",
                    f"GIT_COMMITTER_EMAIL={shlex.quote(email)}"]
    if github.get("ssh_key"):
        ssh = f"ssh -i {github['ssh_key']} -o IdentitiesOnly=yes"
        exports.append(f"GIT_SSH_COMMAND={shlex.quote(ssh)}")
    if not exports:
        return
    command = "export " + " ".join(exports) + "; " + event["tool_input"]["command"]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": dict(event["tool_input"], command=command)}}))


def main():
    event = json.load(sys.stdin)
    log = os.environ.get("AGENTIC_HOOK_LOG")
    if log:
        with open(log, "a") as f:
            f.write(json.dumps(event) + "\n")
    if dry_run(event.get("cwd", ".")):
        check_dry_run(event)
    agent = agent_name(event)
    if not agent:
        return
    tool = event.get("tool_name")
    if tool in ("Edit", "Write"):
        check_file(agent, event)
    elif tool == "Bash":
        check_command(agent, event)
        if agent in AGENTS:
            run_as_account(agent, event)


if __name__ == "__main__":
    main()
