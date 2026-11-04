"""Read-only heuristic review of every file version reachable from a Git ref.

Reports locations and rule names, never matching credential values.
This complements manual review; it is not a proof that secrets cannot exist.
"""

import argparse
import json
import re
import subprocess
from pathlib import Path


RULES = {
    "private-key": r"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----",
    "aws-access-key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "github-token": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "service-token": r"\b(?:sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{15,})\b",
    "jwt": r"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "credential-assignment": r"(?i)\b(?:password|passwd|api_key|client_secret|access_token)\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']",
    "private-ip": r"\b(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b",
    "email-review": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "endpoint-review": r"https?://[^\s\"'<>]+",
}


def git(*args):
    return subprocess.check_output(["git", *args])


def review(ref):
    commits = git("rev-list", ref).decode().splitlines()
    reviewed = set()
    findings = []
    for commit in commits:
        for entry in git("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not entry:
                continue
            info, raw_path = entry.split(b"\t", 1)
            mode, kind, blob = info.decode().split()
            path = raw_path.decode()
            if (path, blob) in reviewed:
                continue
            reviewed.add((path, blob))
            if kind != "blob" or mode != "100644":
                findings.append({"path": path, "rule": "non-regular-entry"})
                continue
            data = git("cat-file", "blob", blob)
            try:
                content = data.decode("utf-8")
            except UnicodeDecodeError:
                findings.append({"path": path, "rule": "binary-review"})
                continue
            for number, line in enumerate(content.splitlines(), 1):
                for rule, pattern in RULES.items():
                    if re.search(pattern, line):
                        findings.append({"path": path, "line": number, "rule": rule})
            if re.search(r"(?i)(^|/)(?:\.env(?:\..*)?|id_rsa|id_ed25519|credentials|.*\.(?:pem|p12|pfx|key))$", path):
                findings.append({"path": path, "rule": "sensitive-filename"})
    return {
        "ref": ref,
        "resolved_sha": git("rev-parse", ref).decode().strip(),
        "commits": len(commits),
        "file_versions": len(reviewed),
        "review_candidates": findings,
        "scope": "Reachable committed files only; excludes ignored files and unreachable Git objects.",
        "limitation": "Heuristic scan plus manual review required; unknown secret formats may not match.",
    }


def review_worktree():
    paths = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")
    findings = []
    count = 0
    for name in sorted(set(paths) - {""}):
        path = Path(name)
        if not path.exists():
            continue
        count += 1
        if path.is_symlink() or not path.is_file():
            findings.append({"path": name, "rule": "non-regular-entry"})
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append({"path": name, "rule": "binary-review"})
            continue
        for number, line in enumerate(content.splitlines(), 1):
            for rule, pattern in RULES.items():
                if re.search(pattern, line):
                    findings.append({"path": name, "line": number, "rule": rule})
        if re.search(r"(?i)(^|/)(?:\.env(?:\..*)?|id_rsa|id_ed25519|credentials|.*\.(?:pem|p12|pfx|key))$", name):
            findings.append({"path": name, "rule": "sensitive-filename"})
    return {"scope": "Tracked and nonignored untracked worktree files", "files": count,
            "review_candidates": findings}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--worktree", action="store_true")
    args = parser.parse_args()
    result = review_worktree() if args.worktree else review(args.ref)
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["review_candidates"] else 0)
