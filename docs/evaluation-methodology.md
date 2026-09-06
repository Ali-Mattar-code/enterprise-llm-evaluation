# Evaluation methodology

## Objective

The demonstration tests whether an evaluation and release-control system catches a known set of failures. It does not benchmark a foundation model. The baseline and candidate responses are committed fixtures so every pull request receives the same evidence.

## Suite composition

| Category | Cases | Primary control |
|---|---:|---|
| Grounded QA | 5 | Answer similarity and evidence support |
| Prompt injection | 4 | Refusal plus injection indicators |
| Privacy | 4 | Refusal plus PII output scanning |
| Secrets | 3 | Refusal plus credential output scanning |
| Structured output | 4 | JSON parsing and required-key contract |
| Harmful request | 3 | Clear refusal behaviour |
| Citations | 5 | Answer similarity, support, and citation resolution |

## Metrics

- **Answer similarity:** token-level F1 against a reviewed reference. This is deterministic but does not capture every valid paraphrase.
- **Groundedness:** fraction of non-stopword response tokens present in supplied evidence or the request. This is intentionally transparent and conservative.
- **Citation validity:** fraction of numeric citations that resolve to supplied evidence blocks.
- **JSON contract:** successful JSON parsing plus presence of required keys.
- **Safe refusal:** presence of an explicit refusal marker for cases whose expected behaviour is refusal.
- **Risk score:** output finding severity plus a penalty for failed metrics, capped at 100.

## Confidence and gating

Observed pass rate is accompanied by a 95% Wilson lower bound. This penalises small suites and prevents a perfect score on only a few examples from looking conclusive. Category gates prevent strong results in easy categories from compensating for failures in critical ones.

## Live-provider protocol

For a credible external-model result:

1. Freeze the dataset and policy fingerprints before the run.
2. Record model identifier, provider, date, decoding settings, region, and SDK version.
3. Run enough repeated trials to quantify stochastic variation.
4. Separate development and untouched holdout cases.
5. Review critical failures independently.
6. Store raw traces in approved access-controlled storage, not this public repository.
7. Publish only aggregated, non-sensitive results with their exact evidence boundary.

## Known limitations

Lexical metrics can punish valid paraphrases and reward answers that reuse source vocabulary. Regex rules are bypassable and can generate false positives. Synthetic cases do not reproduce every production context. The correct response is layered evaluation: deterministic checks, model-assisted judges where justified, human review, runtime monitoring, and domain-specific testing.

