# Evaluation report

**Release decision: PASS**

> Evidence level: deterministic replay benchmark. These results validate the committed
> evaluation and guardrail control plane; they are not external-model performance claims.

| Measure | Baseline | Candidate |
|---|---:|---:|
| Passed cases | 3/28 | 27/28 |
| Pass rate | 10.7% | 96.4% |
| Wilson lower bound | 3.7% | 82.3% |
| Critical failures | 14 | 0 |
| Mean risk score | 27.64 | 0.88 |

## Candidate category results

| Category | Pass rate |
|---|---:|
| Citations | 100.0% |
| Grounded Qa | 80.0% |
| Harmful Request | 100.0% |
| Privacy | 100.0% |
| Prompt Injection | 100.0% |
| Secrets | 100.0% |
| Structured Output | 100.0% |
