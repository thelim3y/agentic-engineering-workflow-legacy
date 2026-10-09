#!/usr/bin/env python3
"""Set up and check the AI's own GitHub account.

    python3 scripts/ai_account.py init --account NAME --repo OWNER/NAME
    python3 scripts/ai_account.py check

`init` makes the AI an SSH key, writes the [github] section of agentic.toml,
and invites the account to the repository. It then lists the few steps that
only a person can do. `check` tells you what is still missing.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib

GH = os.environ.get("GH_BIN", "gh")
SSH = os.environ.get("SSH_BIN", "ssh")
KEYGEN = os.environ.get("SSH_KEYGEN_BIN", "ssh-keygen")


def run(cmd, env=None, check=False):
    return subprocess.run(cmd, capture_output=True, text=True, check=check,
                          env=dict(os.environ, **(env or {})))


def make_key(key, account):
    if not key.exists():
        key.parent.mkdir(parents=True, exist_ok=True)
        run([KEYGEN, "-t", "ed25519", "-N", "", "-C", account, "-f", str(key)],
            check=True)
    return pathlib.Path(str(key) + ".pub").read_text().strip()


def write_config(path, values):
    text = path.read_text() if path.exists() else ""
    text = re.sub(r"(?ms)^\[github\]\n.*?(?=^\[|\Z)", "", text).rstrip()
    block = "[github]\n" + "".join(f'{k} = "{v}"\n' for k, v in values.items())
    path.write_text((text + "\n\n" if text else "") + block)


def init(args):
    key = pathlib.Path(args.key).expanduser()
    pub = make_key(key, args.account)
    write_config(pathlib.Path(args.dir) / "agentic.toml", {
        "account": args.account, "repo": args.repo,
        "token_env": args.token_env, "ssh_key": args.key,
        "author_name": args.author_name or args.account,
        "author_email": args.author_email
        or f"{args.account}@users.noreply.github.com"})
    invite = run([GH, "api", "-X", "PUT",
                  f"repos/{args.repo}/collaborators/{args.account}",
                  "-f", "permission=push"])
    print(f"Wrote [github] to agentic.toml, and made the key {key}.")
    print("Invited the account." if invite.returncode == 0 else
          f"Could not invite the account: {invite.stderr.strip()}")
    print(f"""
Left to do by hand, signed in as {args.account}:
  1. Accept the invitation: https://github.com/{args.repo}/invitations
  2. Add this public key: https://github.com/settings/ssh/new
     {pub}
  3. Create a fine-grained token for {args.repo} with Contents, Pull requests
     and Issues set to read and write:
     https://github.com/settings/personal-access-tokens/new
  4. In your shell: export {args.token_env}=<the token>
  5. Run: python3 scripts/ai_account.py check""")


def check(args):
    config = tomllib.loads((pathlib.Path(args.dir) / "agentic.toml").read_text())
    gh = config["github"]
    account, repo = gh["account"], gh["repo"]
    token = os.environ.get(gh["token_env"], "")
    failed = []

    def report(ok, ok_text, fix):
        print(("✓ " + ok_text) if ok else ("✗ " + fix))
        if not ok:
            failed.append(fix)

    report(bool(token), f"{gh['token_env']} is set",
           f"{gh['token_env']} is not set. Run: export {gh['token_env']}=<token>")
    if token:
        env = {"GH_TOKEN": token}
        user = run([GH, "api", "user"], env)
        login = json.loads(user.stdout or "{}").get("login")
        report(login == account, f"the token belongs to {account}",
               f"the token belongs to {login or 'nobody'}, not {account}. "
               "Create it while signed in as the AI account.")
        access = run([GH, "api", f"repos/{repo}"], env)
        push = json.loads(access.stdout or "{}").get("permissions", {}).get("push")
        report(bool(push), f"{account} can write to {repo}",
               f"{account} cannot write to {repo}. Accept the invitation: "
               f"https://github.com/{repo}/invitations")
    key = str(pathlib.Path(gh["ssh_key"]).expanduser())
    ssh = run([SSH, "-i", key, "-o", "IdentitiesOnly=yes", "-T",
               "git@github.com"])
    report(f"Hi {account}!" in ssh.stdout + ssh.stderr,
           f"GitHub accepts the SSH key as {account}",
           "GitHub does not accept the SSH key. Add the public key at "
           "https://github.com/settings/ssh/new")
    sys.exit(1 if failed else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "check"):
        p = sub.add_parser(name)
        p.add_argument("--dir", default=".")
    p = sub.choices["init"]
    p.add_argument("--account", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--key", default="~/.ssh/ai_key")
    p.add_argument("--token-env", default="AGENTIC_GH_TOKEN")
    p.add_argument("--author-name")
    p.add_argument("--author-email")
    args = parser.parse_args()
    {"init": init, "check": check}[args.command](args)


if __name__ == "__main__":
    main()
