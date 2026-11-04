# Secure Code Controls Lab

Application push, PR, and main release callers invoke a fixed central reusable
workflow commit. That workflow checks out application content into `target`
and trusted central controls into `controls` at a separate immutable revision.
Python isolated mode executes only the controls validator. Target files are
read as text/JSON; application scripts, hooks, installers, and builds are not run.
The job uses ubuntu-latest and contents: read. No secrets are inherited.

The central registry binds application ID, repository name/ID, service, owner,
environment, and criticality. Current registry records are offline fixtures.
Every real binding requires a reviewed central change and refreshed pins.

For PR events, the head SHA identifies the contributor commit. GitHub validation
SHA normally identifies the synthetic test merge with the target branch. The
tested SHA is obtained from the actual checkout. On a main push, release evidence
must instead match the actual main SHA. These are not interchangeable.

Checks from reusable workflows may have composite names. Observe the actual
Checks API name before making it required; the old standalone appsec-pr-gate
name must not be assumed to be the emitted name.

Centralization alone does not force an application contributor to call the
workflow. A replacement passing job can undermine name-based checks. Production
requires an independent mandatory control/publisher and protected central review.
