import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_codeowners_covers_security_controls():
    lines = (ROOT / ".github/CODEOWNERS").read_text().splitlines()
    entries = dict(line.split(maxsplit=1) for line in lines if line and not line.startswith("#"))
    for path in ("*", "/.github/CODEOWNERS", "/.github/workflows/", "/application.json", "/config/", "/scripts/"):
        assert entries[path] == "@kfise"


def test_proposed_ruleset_is_main_only_and_no_bypass():
    rules = json.loads((ROOT / "docs/governance/main-ruleset.proposed.json").read_text())
    assert rules["conditions"] == {"ref_name": {"include": ["refs/heads/main"], "exclude": []}}
    assert rules["enforcement"] == "active"
    assert rules["bypass_actors"] == []
    by_type = {rule["type"]: rule for rule in rules["rules"]}
    pr = by_type["pull_request"]["parameters"]
    assert pr["required_approving_review_count"] == 1
    assert pr["require_code_owner_review"] is True
    assert pr["dismiss_stale_reviews_on_push"] is True
    assert pr["require_last_push_approval"] is True
    assert {"deletion", "non_fast_forward"} <= set(by_type)
    check = by_type["required_status_checks"]["parameters"]
    assert check["strict_required_status_checks_policy"] is True
    assert check["required_status_checks"] == [{"context": "appsec-pr-gate / security-validation", "integration_id": 15368}]
