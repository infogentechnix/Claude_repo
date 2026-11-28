#!/usr/bin/env python3
"""PreToolUse Bash gate: block installing a remote repo until SkillSpector has scanned it.

Gated commands: git clone / git submodule add, pip|uv|pipx installs from git+URL,
npm/npx/pnpm/yarn/bun installs from GitHub, curl|wget piped to a shell, and
`claude plugin marketplace add`. A repo is allowed once `skillspector/scan.sh`
has recorded it in .claude/skillspector/scanned.log.

`--key <target>` prints the normalised log key for a target (used by scan.sh).
Set SKILLSPECTOR_GATE=off to disable the gate.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / ".claude" / "skillspector" / "scanned.log"

PIPE_TO_SHELL = re.compile(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z)?sh\b")
INSTALL_CMD = re.compile(
    r"\bgit\s+(clone|submodule\s+add)\b"
    r"|\b(pip3?|uv\s+pip|uv\s+tool|uvx|pipx|uv\s+add|poetry\s+add)\b.*\bgit\+"
    r"|\b(npm|pnpm|yarn|bun)\s+(i|install|add)\b.*(github:|github\.com)"
    r"|\b(npx|bunx|pnpm\s+dlx)\b.*(github:|github\.com)"
    r"|\bplugin\s+(marketplace\s+add|install)\b"
    r"|" + PIPE_TO_SHELL.pattern
)
URL = re.compile(r"(?:git\+)?(?:https?://|ssh://|git@)([\w.-]+)[/:]([\w.-]+)/([\w.-]+)")
GH_SHORT = re.compile(r"github:([\w.-]+)/([\w.-]+)")
RAW_GH = re.compile(r"raw\.githubusercontent\.com/([\w.-]+)/([\w.-]+)")
MARKETPLACE = re.compile(r"marketplace\s+add\s+([\w.-]+)/([\w.-]+)")


def _norm(host: str, owner: str, repo: str) -> str:
    repo = re.sub(r"(\.git)?([#@].*)?$", "", repo)
    return f"{host.lower()}/{owner.lower()}/{repo.lower()}"


def key_for(target: str) -> str:
    """Normalise a URL, shorthand or local path to the key stored in the log."""
    if m := RAW_GH.search(target):
        return _norm("github.com", m[1], m[2])
    if m := URL.search(target):
        return _norm(m[1], m[2], m[3])
    if m := GH_SHORT.search(target):
        return _norm("github.com", m[1], m[2])
    return "path:" + os.path.realpath(os.path.expanduser(target))


def repos_in(cmd: str) -> set[str]:
    keys = {_norm("github.com", m[1], m[2]) for m in RAW_GH.finditer(cmd)}
    keys |= {_norm(m[1], m[2], m[3]) for m in URL.finditer(cmd)
             if m[1].lower() != "raw.githubusercontent.com"}
    keys |= {_norm("github.com", m[1], m[2]) for m in GH_SHORT.finditer(cmd)}
    keys |= {_norm("github.com", m[1], m[2]) for m in MARKETPLACE.finditer(cmd)}
    return keys


def scanned() -> set[str]:
    try:
        return {line.split("\t", 1)[0] for line in LOG.read_text().splitlines() if line.strip()}
    except OSError:
        return set()


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--key":
        print(key_for(sys.argv[2]))
        return 0
    if os.environ.get("SKILLSPECTOR_GATE", "").lower() == "off":
        return 0
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    if not cmd or "skillspector/scan.sh" in cmd or not INSTALL_CMD.search(cmd):
        return 0

    repos = repos_in(cmd)
    if not repos:
        if PIPE_TO_SHELL.search(cmd):
            deny("SkillSpector gate: piping a download into a shell is blocked. Download the script "
                 "to a file, scan it with `bash skillspector/scan.sh <file>`, read it, then run it.")
        return 0

    missing = sorted(repos - scanned())
    if missing:
        deny("SkillSpector gate: scan before installing. Not yet scanned: " + ", ".join(missing) + ". "
             "Run `bash skillspector/scan.sh <repo-url>` for each, review the findings with the user "
             "(see the skill-inspector skill), then retry. Do not install a DO_NOT_INSTALL verdict unless the "
             "user explicitly accepts it (`bash skillspector/scan.sh --accept <url>`).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
