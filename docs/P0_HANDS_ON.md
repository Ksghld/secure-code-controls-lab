# P0 Hands-on Walkthrough

This walkthrough is intentionally local-first. Publishing a repository and changing GitHub rules require separate approval.

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
and draft-PR helpers. Do not establish a new authentication method, publish
credentials, push protected main, or merge without human review. Helper interfaces
are environment-specific and must be discovered from approved documentation.

## 4. Verify successful and failed PR checks

For a clean PR, `appsec-pr-gate` should complete successfully. Add a critical marker and push another commit; the existing PR receives a synchronize event and the gate should fail. Remove the marker and push again to restore a successful check.

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
4. Require one independent approving review. Enable stale-review dismissal or latest-reviewable-push approval when available.
5. Require the exact emitted check name observed in the Checks API, from GitHub Actions. Reusable workflow job names may be composite; do not assume the caller name alone.
6. Restrict force pushes and branch deletion; minimize bypass actors.

Do not require PRs or checks on every feature branch. The push monitor observes pushes after they occur; it cannot prevent the push itself.

The Ruleset applies because `main` is the PR's target/base branch. It does not lock or require checks on the source feature branch itself. Feature branches remain unrestricted for normal development.

## 6. Verify direct push restriction

Direct-push negative tests require a separate authorized administrative exercise.
The execution agent must not attempt protected-main pushes. Record the test as
NOT_VERIFIED until the authorized administrator supplies actual denial evidence.

Without a second real reviewer, independent four-eyes behavior remains `NOT_VERIFIED`.
