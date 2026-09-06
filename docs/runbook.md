# Operational runbook

## Before a release

1. Confirm the dataset, prompt, and policy fingerprints.
2. Run unit tests and the deterministic demonstration.
3. Execute an approved live-provider evaluation when the release changes model behaviour.
4. Inspect every critical failure and all cases routed to human review.
5. Record the gate configuration with the release artifact.

## Gate failure

| Failure | First response |
|---|---|
| Critical safety case | Block release; inspect raw response and connected-tool permissions |
| Category minimum | Cluster failures by attack and expected behaviour; add a regression case |
| Wilson lower bound | Increase representative sample size; do not weaken the confidence gate merely to ship |
| Latency | Separate provider latency, retries, retrieval, and evaluator overhead |
| Cost | Inspect token growth, repeated calls, judge-model use, and caching policy |
| Risk score | Identify whether findings are concentrated or systemic |

## Incident response

1. Disable the affected capability or revert to the last approved model/prompt version.
2. Preserve traces in access-controlled storage.
3. Revoke exposed credentials and notify the responsible security owner.
4. Add a minimal, sanitised regression case.
5. Correct the application control, rerun the full suite, and require explicit approval.
6. Document the evidence boundary and any remaining exposure.

## Scaling beyond the demonstration

- move review storage to Postgres with role-based access;
- send traces through the organisation's telemetry pipeline;
- encrypt data in transit and at rest;
- use a secrets manager and short-lived credentials;
- separate evaluator and production-model permissions;
- add multilingual, multimodal, tool-use, and business-specific holdout suites;
- establish owners and expiry dates for every exception.

