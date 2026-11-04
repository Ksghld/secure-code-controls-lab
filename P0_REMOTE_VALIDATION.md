# Remote Validation Ledger

Status: NOT_EXECUTED. No publication, PR URL, workflow run URL, or remote SHA exists.
Local tests cannot establish remote enforcement.

| Exercise | Actual result | Evidence |
| --- | --- | --- |
| Feature Push Monitoring | NOT_EXECUTED | None |
| Clean PR / central reusable workflow | NOT_EXECUTED | None |
| Exact required check/source on main | NOT_EXECUTED | None |
| Critical finding and denied merge | NOT_EXECUTED | None |
| Direct protected-main push rejected | NOT_EXECUTED | Separate administrator exercise required |
| New PR commit requires fresh check | NOT_EXECUTED | None |
| Scanner error fails closed remotely | NOT_EXECUTED | None |
| Invalid ownership fails remotely | NOT_EXECUTED | None |
| Human merge and actual main SHA validation | NOT_EXECUTED | None |
| Synthetic digest mismatch fails release | NOT_EXECUTED | None |
| Caller tampering / same-name check bypass | NOT_EXECUTED | Offline illustration only |
| Independent review | NOT_EXECUTED | Two authorized identities required |

## Read-only evidence collection after authorized publication

These public REST GET paths require no new authentication setup. Use an approved
read-only API mechanism; never include credentials in reports:

```text
GET /repos/Ksghld/secure-code-controls-lab/actions/runs
GET /repos/Ksghld/secure-code-controls-lab/pulls/PR_NUMBER
GET /repos/Ksghld/secure-code-controls-lab/commits/SHA/check-runs
GET /repos/Ksghld/secure-code-controls-lab/commits/SHA/status
GET /repos/Ksghld/secure-code-controls-lab/rules/branches/main
GET /repos/Ksghld/secure-code-controls-lab/rulesets?includes_parents=true
GET /repos/Ksghld/secure-code-controls-lab/rulesets/RULESET_ID
```

Replace placeholders from observed PR/run data. Follow pagination. Record check
name, app.id/app.slug, head_sha, conclusion, details_url, PR head/base/merge SHA,
run event/head_sha/attempt and central revision. Record effective rule context and
integration_id, target matching, enforcement, and bypass actors. Verify the source
ID corresponds to GitHub Actions. Do not infer required checks from YAML job names.

The administrator enables a repository branch ruleset for main: require PR and the
observed check, select GitHub Actions, prevent deletion/force push, minimize bypass,
and require independent/stale-dismissed review where supported. Recheck effective rules.
For negative demonstrations, retain the failing PR and mergeability response;
an authorized human tests denial without disabling rules. The agent must not merge
or push protected main. A new commit must invalidate old SHA evidence.

Branch rulesets are available for eligible public repositories; this is distinct from
push rulesets. GitHub's repository ruleset documentation is the authoritative reference.
Availability does not prove this lab's settings.

For caller tampering, use a separately authorized disposable PR proposing a same-name
passing job without the central call. Record actual Checks API identity and enforcement
outcome; never merge that change. Required GitHub Actions source alone is not integrity
proof. Production needs independent enforcement and security-controlled review.
