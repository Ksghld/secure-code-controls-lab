# P0 Hands-on Walkthrough

This walkthrough separates local synthetic exercises from actual hosted controls.
See P0_REMOTE_VALIDATION.md for observed results and pending acceptance tests.

## 1. Understand the Git operations

- `git commit` records a local snapshot and parent relationship.
- `git push` transfers local commits to a remote branch. It does not create a Pull Request.
- A Pull Request asks GitHub to compare a head branch with a target/base branch and review a proposed merge.
- Another push to the same PR head branch normally emits `pull_request:synchronize` and reruns the PR gate.
- Merge creates or selects the commit that reaches the target branch. The resulting release SHA is not assumed to equal the PR test-merge SHA or the PR head SHA.

## 2. Run the local scanner

```bash
python scripts/mock_appsec.py --mode monitor --output reports/push-scan.json
python scripts/mock_appsec.py --mode enforce --output reports/pr-scan.json
```

Both commands pass on the clean baseline.

Add one synthetic marker to `src/demo.txt`:

```text
SIMULATED_CRITICAL_SAST
```

Then run both commands again. Monitor returns zero but reports a critical observation. Enforce returns exit code 2. Remove the marker afterward.

Simulate a tool failure:

```bash
python scripts/mock_appsec.py --mode enforce --simulate-error --output reports/error.json
```

It returns exit code 3 and writes `tool_error: true`; it never reports a clean scan.

## 3. Publish only after approval

```bash
git switch -c codex/clean-pr
echo "harmless change" >> src/demo.txt
git add src/demo.txt
git commit -m "Add harmless demo change"
```

Repository creation and initial branch bootstrap are administrator operations.
Use the environment's approved isolated worktree, broker-backed feature push,
and ready-for-review PR helpers. Do not establish a new authentication method, publish
credentials, push protected main, or merge without human review. Helper interfaces
are environment-specific and must be discovered from approved documentation.

## 4. Verify successful and failed PR checks

For a clean PR, the required `appsec-pr-gate / security-validation` check passes.
Use a separate negative PR for a Critical marker and preserve its failed head. Do
not merge it or repair it before capturing the head SHA, run and blocking state.
A repaired PR's current green head is not evidence of a Critical finding being blocked.

The workflow records:

- `GITHUB_SHA`: GitHub's PR test-merge revision for this workflow.
- `pull_request.head.sha`: the contributor's head commit.
- `APPSEC_TESTED_SHA`: `git rev-parse HEAD` from the checked-out content.
- source and target refs.

The post-merge workflow checks the actual SHA on `main`. An old green PR check is not release evidence for a different merged SHA.

## 5. Configure a GitHub Free-compatible ruleset manually

First obtain a real `appsec-pr-gate` check run. Then open:

1. Repository **Settings** -> **Rules** -> **Rulesets**.
2. Create a branch ruleset targeting `main` only and set it active.
3. Require a Pull Request before merging.
4. Require one independent approval, stale-review dismissal, latest-reviewable-push approval and CODEOWNER review after reviewed CODEOWNERS files reach main.
5. Require the exact emitted check name observed in the Checks API, from GitHub Actions. Reusable workflow job names may be composite; do not assume the caller name alone.
6. Restrict force pushes and branch deletion; keep the bypass list empty.

Do not require PRs or checks on every feature branch. The push monitor observes pushes after they occur; it cannot prevent the push itself.

The Ruleset applies because `main` is the PR's target/base branch. It does not lock or require checks on the source feature branch itself. Feature branches remain unrestricted for normal development.

## 6. Verify direct push restriction

Direct-push negative tests require a separate authorized administrative exercise.
The execution agent must not attempt protected-main pushes. Record the test as
NOT_VERIFIED until the authorized administrator supplies actual denial evidence.

Independent review was observed on PR #6. The separate PR #7 stale-approval test
must record APPROVED at the first SHA, DISMISSED after the second reviewable push,
new checks and blocked merge until another human review. Never approve or merge
on the human reviewer's behalf.
