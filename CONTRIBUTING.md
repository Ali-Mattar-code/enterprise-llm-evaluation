# Contributing

Contributions should improve the reliability or clarity of the evaluator without overstating what its evidence proves.

## Development workflow

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,api]"
ruff check .
mypy src/llm_guardian
pytest --cov=llm_guardian
python scripts/run_demo.py --check-clean
```

## Evaluation cases

- Use synthetic or properly authorised data only.
- Give every case a stable, unique identifier.
- State the expected behaviour and severity explicitly.
- Add a regression case for every corrected failure mode.
- Do not remove a difficult case merely to improve the headline score.
- Label replay, synthetic, live-model, and production evidence separately.

## Pull requests

Explain the problem, control change, test evidence, and remaining limitations. Changes to gate thresholds require a rationale; lowering a threshold solely to make a failing candidate pass will not be accepted.

