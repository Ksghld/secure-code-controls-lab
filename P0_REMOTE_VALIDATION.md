# P0 Remote Validation Ledger

Snapshot: 2026-11-09, before the second PR #7 push. This replaces the obsolete
NOT_EXECUTED pre-publication report. Results are observations, not claims of a
production security service. Pending work is explicitly incomplete.

| Control | Observed result | Evidence |
| --- | --- | --- |
| Feature push monitoring | PASS as MJ on 1c29195f6fa224e1d5123b61d42cadb9fed9e2ec | [Run 42530553863](https://github.com/Ksghld/secure-code-controls-lab/actions/runs/42530553863) |
| Central PR gate | PASS; GitHub Actions, appsec-pr-gate / security-validation | [Run 42530559297](https://github.com/Ksghld/secure-code-controls-lab/actions/runs/42530559297) |
| Independent review | MJ authored PR #6, human approved exact head and merged | [PR #6](https://github.com/Ksghld/secure-code-controls-lab/pull/6) |
| Post-merge exact main SHA | PASS for 7184e2e01d97e03257f19bca8c932169bce1e939 | [Run 42480927242](https://github.com/Ksghld/secure-code-controls-lab/actions/runs/42480927242) |
| Active main protection | One approval, stale dismissal, latest-push approval, strict check, no bypass, no force push/deletion | [Ruleset 26795523](https://github.com/Ksghld/secure-code-controls-lab/rules/26795523) |
| Clean but unreviewed PR | PR #7 was blocked with all checks passing and no review | [PR #7](https://github.com/Ksghld/secure-code-controls-lab/pull/7) |
| First review for stale test | APPROVED on 1c29195f6fa224e1d5123b61d42cadb9fed9e2ec | [Review](https://github.com/Ksghld/secure-code-controls-lab/pull/7#pullrequestreview-5823321837) |
| Stale dismissal after second push | PENDING: prepared acd756c4675e62ae9119a4803e170bec188bb37e is not yet remote evidence | Same PR; record both checks and dismissed review after push |
| Missing/invalid ownership | Failed required gate; no merge | [PR #3](https://github.com/Ksghld/secure-code-controls-lab/pull/3), [run](https://github.com/Ksghld/secure-code-controls-lab/actions/runs/41936413531) |
| Scanner error fail-closed | Failed required gate; no merge | [PR #4](https://github.com/Ksghld/secure-code-controls-lab/pull/4), [run](https://github.com/Ksghld/secure-code-controls-lab/actions/runs/42475666523) |
| Fresh Critical finding under Active rules | PENDING fresh negative PR. PR #2's repaired current head passes and is NOT proof | [PR #2](https://github.com/Ksghld/secure-code-controls-lab/pull/2) |
| Direct push denied | Not reverified in this snapshot; authenticated Rules Insights read returned 403. Do not claim new denial evidence | Administrator capture remains required |
| CODEOWNERS enforced | PENDING reviewed files on main, rules change and subsequent MJ PR auto-review request | docs/governance/README.md |
| Central main protection | PENDING; no current ruleset or central-native check observed | central docs/governance/README.md |

## Immutable revisions and identity

- Central reusable workflow: cd778ccf709701f9682c76cedbdd9ab096a0203c.
- Trusted scanner/policy checkout: 76ce1e187c6e01e4cc30eaad75f26fd25f4dc774.
- Verified GitHub Actions expected source: integration 15368.
- Local commit authorship is not proof of pusher identity. Actions actor and PR author
  identify mjopenclawbot[bot] for the MJ test runs above.
- PR head, GitHub synthetic test-merge SHA, and resulting main SHA are distinct.
  Passing a previous revision does not validate a later reviewable push.

## Negative PR disposition

PRs #1-#5 were captured privately with head SHAs, reviews and run URLs before closure.
At this snapshot all five remain open/unmerged. Closure is still pending; do not report
closed until GitHub confirms it. No negative PR may be merged.
The fresh Critical test must remain failing and unmerged. Preserve failures rather
than repair its head and accidentally remove the evidence again.

## Completion protocol

Verify the second PR #7 push, dismissed review and fresh checks; stop for independent
review. A human alone approves/merges. Then compare the resulting main SHA with the
release workflow head and checkout/event validation. Never infer deployment or
artifact enforcement from this P0 post-merge validation.
