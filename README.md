# Secure Code Controls Lab

Synthetic application and GitHub Actions callers for a centralized security learning lab.
No application build, deployment, real credentials, or real vulnerability scanning.

## Architecture
- appsec-push.yml monitors every pushed branch; findings cannot undo an accepted push.
- appsec-pr.yml enforces on opened, synchronize, reopened, and ready_for_review events.
- appsec-release.yml validates the actual main checkout SHA and synthetic release correlation.
- All callers reference an immutable central reusable workflow. That workflow separately
  checks out its immutable central scanner/policy revision, using ubuntu-latest and read-only permissions.
- application.json is compared with the centrally approved registry. Synthetic identity
  10001 must be replaced with the authorized public repository ID through reviewed changes.
- src and optional infra are read as untrusted text, never executed. Scan/config errors fail closed.
- The original local P0 scanner/tests remain for learning; GitHub does not execute that scanner.

## Local validation
From the parent of both checkouts:
```text
secure-code-controls-lab\.venv\Scripts\python.exe -m pytest -q secure-code-controls-lab/tests central-security-workflows-lab/tests
```
Install test dependencies from requirements.txt into a local virtual environment if needed.
The scanner itself uses Python's standard library. See README_HE.md and docs/P0_HANDS_ON.md.

## Controls and limits
All branches are monitored; protected merge destinations are enforced.
A repository-level branch ruleset must target main and require the exact composite check
name observed in GitHub's Checks API, with GitHub Actions as expected source.
No such remote enforcement has yet been demonstrated.
A contributor may replace the caller with a passing job of the same name.
Centralization protects scanner content, not mandatory invocation. See ARCHITECTURE.md
and KNOWN_LIMITATIONS.md for recommended independent production enforcement.

Publication requires completed administrator onboarding and a passed content audit.
Use only the approved feature-branch and human-review process. No automatic merge.

