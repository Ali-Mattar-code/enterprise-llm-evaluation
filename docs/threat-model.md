# Threat model

## Assets

- system and developer instructions;
- user and customer data;
- credentials and connected tools;
- model outputs used in business decisions;
- evaluation evidence and release history.

## Adversaries and failures

| Threat | Example impact | Implemented control | Residual risk |
|---|---|---|---|
| Direct prompt injection | Policy bypass or prompt disclosure | Injection rules, refusal tests, category gate | Novel wording and multilingual attacks |
| Indirect injection | Malicious text inside retrieved evidence | Versioned adversarial cases; provider boundary | Requires context-aware isolation in the host application |
| PII exfiltration | Private contact or payment data in output | Output scanning, redaction helper, zero-failure privacy gate | Pattern rules miss unusual formats |
| Secret leakage | API or cloud keys returned to a user | Credential rules and zero-failure secret gate | Unknown credential formats |
| Unsafe tool use | Model executes a high-impact action | Human-review queue and explicit approval field tests | Host application must enforce tool permissions |
| Hallucinated policy | Incorrect answer drives action | Groundedness, references, and citation checks | Lexical support is not semantic truth |
| Evaluation gaming | Changes improve test score but not production quality | Holdouts, fingerprints, failed-case retention | Public fixtures can still be overfit |
| Supply-chain compromise | Malicious dependency or workflow | Minimal dependencies, pinned action majors, read-only CI permissions | Transitive dependency risk remains |

## Non-goals

This repository is not a web-application firewall, compliance certification, content moderation service, or substitute for least-privilege access controls. It provides test and release evidence that can be integrated with those controls.

## Reporting

Do not open public issues containing working credentials, private prompts, customer data, or exploitable production details. Revoke exposed credentials first, then use the repository owner's private contact channel.

