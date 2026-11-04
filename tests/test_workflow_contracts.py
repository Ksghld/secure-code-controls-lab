from pathlib import Path

import yaml
import subprocess


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def load_workflow(name):
    # BaseLoader follows YAML syntax while preserving the GitHub key `on` as text.
    return yaml.load((WORKFLOWS / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def assert_minimal_permissions(workflow):
    assert workflow["permissions"] == {"contents": "read"}


def test_push_monitor_contract():
    workflow = load_workflow("appsec-push.yml")
    assert_minimal_permissions(workflow)
    assert set(workflow["on"]) == {"push"}
    assert not isinstance(workflow["on"]["push"], dict)
    job = workflow["jobs"]["appsec-push-monitor"]
    assert job["name"] == "appsec-push-monitor"
    assert "if" not in job
    assert job["with"]["scan_mode"] == "monitor"
    assert "steps" not in job


def test_pr_gate_contract():
    workflow = load_workflow("appsec-pr.yml")
    assert_minimal_permissions(workflow)
    assert "pull_request_target" not in workflow["on"]
    pull_request = workflow["on"]["pull_request"]
    assert pull_request["types"] == ["opened", "synchronize", "reopened", "ready_for_review"]
    assert "branches" not in pull_request
    assert "paths" not in pull_request
    job = workflow["jobs"]["appsec-pr-gate"]
    assert job["name"] == "appsec-pr-gate"
    assert "if" not in job
    assert job["with"]["scan_mode"] == "enforce"
    assert "steps" not in job


def test_release_verification_contract():
    workflow = load_workflow("appsec-release.yml")
    assert_minimal_permissions(workflow)
    assert workflow["on"]["push"]["branches"] == ["main"]
    job = workflow["jobs"]["appsec-release-verify"]
    assert job["name"] == "appsec-release-verify"
    assert job["with"]["scan_mode"] == "enforce"
    assert "steps" not in job


def test_only_expected_p0_workflows_exist():
    assert {path.name for path in WORKFLOWS.glob("*.yml")} == {
        "appsec-pr.yml",
        "appsec-push.yml",
        "appsec-release.yml",
    }
    for path in WORKFLOWS.glob("*.yml"):
        workflow = load_workflow(path.name)
        for job in workflow["jobs"].values():
            assert job["uses"] == "Ksghld/central-security-workflows-lab/.github/workflows/security-validation.yml@bc29eb95c826c36c029f558e8b817539f880b346"
            assert "secrets" not in job


def test_caller_pin_matches_reviewed_local_central_workflow():
    central = ROOT.parent / "central-security-workflows-lab"
    pin = load_workflow("appsec-pr.yml")["jobs"]["appsec-pr-gate"]["uses"].split("@", 1)[1]
    path = ".github/workflows/security-validation.yml"
    committed = subprocess.check_output(["git", "show", f"{pin}:{path}"], cwd=central)
    assert committed.replace(b"\r\n", b"\n") == (central / path).read_bytes().replace(b"\r\n", b"\n")
