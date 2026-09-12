# Reproducibility checklist

Use this checklist when validating a change to LLM Guardian. It keeps the deterministic replay path separate from live-provider experiments and makes the evidence boundary explicit.

## Fast, offline validation

Run these commands from the repository root:

```bash
python scripts/run_demo.py
pytest
```

The demo should complete without an API key or network request. It exercises the committed evaluation cases, release-gate policy, and generated evidence artifacts.

## Optional integration paths

Install only the extra you need before exercising a live provider or interface:

```bash
python -m pip install -e ".[openai]"
python -m pip install -e ".[api,dashboard]"
```

Live-provider runs are not interchangeable with the deterministic demo. Record the provider, model, dataset revision, policy configuration, and environment used for any external result.

## Evidence to retain

For a reviewable run, keep:

- the exact commit SHA;
- the dataset and configuration paths;
- the provider mode (`replay` or a named live adapter);
- the generated comparison and report artifacts;
- the test and lint commands used;
- any non-default environment variables, excluding their values.

Never commit API keys, personal data, customer data, or unredacted provider responses.

## Interpreting failures

- A failing replay test is a regression in the local control plane until proven otherwise.
- A live-provider failure may be caused by credentials, rate limits, provider drift, or network conditions; do not present it as a deterministic repository failure without reproducing it offline.
- A passing release gate means only that the configured suite and policy passed. It is not evidence that an application is safe, compliant, or representative of production traffic.
