import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "mock_appsec.py"
MARKERS = {
    "SIMULATED_CRITICAL_SCA": "sca",
    "SIMULATED_CRITICAL_SECRET": "secrets",
    "SIMULATED_CRITICAL_IAC": "iac",
    "SIMULATED_CRITICAL_SAST": "sast",
}


def run_scanner(tmp_path: Path, mode: str, text: str = "clean", *extra: str):
    source = tmp_path / "src"
    source.mkdir(exist_ok=True)
    (source / "demo.txt").write_text(text, encoding="utf-8")
    output = tmp_path / "reports" / "scan.json"
    env = os.environ.copy()
    env.update(
        {
            "GITHUB_REPOSITORY": "synthetic/secure-code-controls-lab",
            "GITHUB_EVENT_NAME": "pull_request" if mode == "enforce" else "push",
            "GITHUB_SHA": "merge-sha-123",
            "APPSEC_TESTED_SHA": "tested-sha-456",
            "PR_HEAD_SHA": "head-sha-789",
            "GITHUB_HEAD_REF": "feature/demo",
            "GITHUB_BASE_REF": "main",
            "SOURCE_DATE_EPOCH": "1704067200",
        }
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCANNER),
            "--mode",
            mode,
            "--output",
            str(output),
            "--repo-root",
            str(tmp_path),
            *extra,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, json.loads(output.read_text(encoding="utf-8"))


def test_clean_enforcement_passes(tmp_path):
    result, report = run_scanner(tmp_path, "enforce")
    assert result.returncode == 0
    assert report["status"] == "clean"
    assert report["critical_count"] == 0
    assert report["tested_sha"] == "tested-sha-456"
    assert report["github_event_sha"] == "merge-sha-123"
    assert report["pr_head_sha"] == "head-sha-789"
    assert report["simulated"] is True
    assert report["tool_error"] is False


@pytest.mark.parametrize("marker,engine", MARKERS.items())
def test_each_critical_marker_blocks_enforcement(tmp_path, marker, engine):
    result, report = run_scanner(tmp_path, "enforce", marker)
    assert result.returncode == 2
    assert report["status"] == "blocked"
    assert report["critical_count"] == 1
    assert report["findings"][0]["engine"] == engine
    assert report["findings"][0]["marker"] == marker


def test_monitor_reports_critical_findings_without_policy_block(tmp_path):
    result, report = run_scanner(tmp_path, "monitor", "\n".join(MARKERS))
    assert result.returncode == 0
    assert report["status"] == "critical_observed"
    assert report["critical_count"] == 4


def test_simulated_scanner_error_fails_and_is_not_clean(tmp_path):
    result, report = run_scanner(tmp_path, "enforce", "clean", "--simulate-error")
    assert result.returncode == 3
    assert report["status"] == "tool_error"
    assert report["tool_error"] is True
    assert "MOCK_APPSEC_TOOL_ERROR" in result.stderr


def test_scanner_does_not_scan_its_own_marker_definitions(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "not-a-target.py").write_text("SIMULATED_CRITICAL_SAST", encoding="utf-8")
    result, report = run_scanner(tmp_path, "enforce")
    assert result.returncode == 0
    assert report["critical_count"] == 0
