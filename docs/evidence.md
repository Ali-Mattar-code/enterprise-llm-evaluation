# Evidence record

## Committed demonstration

- **Evidence type:** deterministic replay benchmark
- **Suite:** 28 synthetic cases in `datasets/evaluation_suite.jsonl`
- **Policy:** `configs/release_gate.yaml`
- **Command:** `python scripts/run_demo.py`
- **Outputs:** `artifacts/demo/comparison.json` and `artifacts/demo/report.md`
- **External API calls:** none
- **Paid services:** none
- **Real customer data:** none

The fixture includes reserved-domain email addresses, recognised test card numbers, and clearly labelled non-working credential strings. They exist only to test detection and must never be replaced with real values.

## Result boundary

The 96.4% candidate pass rate means that the committed evaluator classifies 27 of 28 committed candidate fixtures as passing. It must not be described as the measured performance of a named external model or a production customer deployment.

The single failing case is preserved in the public suite. The release passes because the failure is non-critical, the grounded-QA category remains at its configured minimum, and all critical categories pass completely.

## Reproduction

```bash
python -m pip install -e ".[dev]"
python scripts/run_demo.py
pytest
```

CI reruns the same gate on every push and pull request. Live model experiments should write to `artifacts/local/`, which is excluded from version control by default.

