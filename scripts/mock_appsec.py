#!/usr/bin/env python3
"""Deterministic synthetic AppSec scanner used only by this learning lab."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


MARKERS = {
    "SIMULATED_CRITICAL_SCA": "sca",
    "SIMULATED_CRITICAL_SECRET": "secrets",
    "SIMULATED_CRITICAL_IAC": "iac",
    "SIMULATED_CRITICAL_SAST": "sast",
}
SCAN_DIRECTORIES = ("src", "infra")
SCAN_FILES = ("app.yaml",)


def utc_timestamp() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        moment = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    else:
        moment = datetime.now(timezone.utc)
    return moment.isoformat().replace("+00:00", "Z")


def read_event_payload() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    try:
        with open(event_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def git_head(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "LOCAL_UNCOMMITTED"


def metadata(repo_root: Path) -> dict[str, str]:
    payload = read_event_payload()
    pull_request = payload.get("pull_request") or {}
    head = pull_request.get("head") or {}
    base = pull_request.get("base") or {}
    tested_sha = (
        os.environ.get("APPSEC_TESTED_SHA")
        or os.environ.get("GITHUB_SHA")
        or git_head(repo_root)
    )
    return {
        "repo": os.environ.get("GITHUB_REPOSITORY", f"local/{repo_root.name}"),
        "event": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "tested_sha": tested_sha,
        "github_event_sha": os.environ.get("GITHUB_SHA", tested_sha),
        "pr_head_sha": os.environ.get("PR_HEAD_SHA") or head.get("sha", ""),
        "source_branch": (
            os.environ.get("GITHUB_HEAD_REF")
            or head.get("ref")
            or os.environ.get("GITHUB_REF_NAME", "local")
        ),
        "target_branch": os.environ.get("GITHUB_BASE_REF") or base.get("ref", ""),
    }


def is_within(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def scan_targets(repo_root: Path) -> Iterable[Path]:
    for relative in SCAN_FILES:
        candidate = repo_root / relative
        if candidate.is_file() and not candidate.is_symlink() and is_within(candidate, repo_root):
            yield candidate
    for relative in SCAN_DIRECTORIES:
        directory = repo_root / relative
        if not directory.is_dir() or directory.is_symlink():
            continue
        for candidate in sorted(directory.rglob("*")):
            if candidate.is_file() and not candidate.is_symlink() and is_within(candidate, repo_root):
                yield candidate


def find_markers(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for candidate in scan_targets(repo_root):
        relative = candidate.relative_to(repo_root).as_posix()
        text = candidate.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for marker, engine in MARKERS.items():
                if marker in line:
                    findings.append(
                        {
                            "engine": engine,
                            "severity": "critical",
                            "marker": marker,
                            "path": relative,
                            "line": line_number,
                        }
                    )
    return findings


def build_report(
    repo_root: Path,
    mode: str,
    findings: list[dict[str, Any]],
    tool_error: bool,
) -> dict[str, Any]:
    evidence = metadata(repo_root)
    critical_count = len(findings)
    if tool_error:
        status = "tool_error"
    elif critical_count and mode == "enforce":
        status = "blocked"
    elif critical_count:
        status = "critical_observed"
    else:
        status = "clean"
    return {
        "schema_version": 1,
        **evidence,
        "executed_engines": sorted(set(MARKERS.values())),
        "mode": mode,
        "findings": findings,
        "critical_count": critical_count,
        "status": status,
        "tool_error": tool_error,
        "simulated": True,
        "timestamp_utc": utc_timestamp(),
    }


def write_report(output: Path, report: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("monitor", "enforce"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--simulate-error", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if args.simulate_error:
        report = build_report(repo_root, args.mode, [], tool_error=True)
        write_report(args.output, report)
        print("MOCK_APPSEC_TOOL_ERROR simulated=true", file=sys.stderr)
        return 3

    try:
        findings = find_markers(repo_root)
        report = build_report(repo_root, args.mode, findings, tool_error=False)
        write_report(args.output, report)
    except Exception as error:  # The tool must fail visibly, never report a clean scan.
        report = build_report(repo_root, args.mode, [], tool_error=True)
        write_report(args.output, report)
        print(f"MOCK_APPSEC_TOOL_ERROR type={type(error).__name__}", file=sys.stderr)
        return 3

    print(
        f"MOCK_APPSEC mode={args.mode} status={report['status']} "
        f"critical_count={report['critical_count']} simulated=true"
    )
    for finding in findings:
        print(
            "FINDING "
            f"engine={finding['engine']} severity=critical "
            f"path={finding['path']} line={finding['line']} marker={finding['marker']}"
        )
    if args.mode == "enforce" and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
