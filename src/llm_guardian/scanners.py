from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Finding, Severity


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    message: str
    severity: Severity


INJECTION_RULES = (
    Rule(
        "instruction_override",
        re.compile(r"\b(ignore|disregard|forget)\b.{0,50}\b(previous|prior|system)\b", re.I),
        "Possible attempt to override trusted instructions.",
        Severity.HIGH,
    ),
    Rule(
        "system_prompt_extraction",
        re.compile(
            r"\b(reveal|print|repeat|show)\b.{0,40}\b(system prompt|hidden instructions)\b",
            re.I,
        ),
        "Possible system-prompt extraction attempt.",
        Severity.CRITICAL,
    ),
    Rule(
        "encoded_payload",
        re.compile(r"\b(base64|rot13|decode this payload)\b", re.I),
        "Encoded content requires additional inspection.",
        Severity.MEDIUM,
    ),
)

PII_RULES = (
    Rule(
        "email_address",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
        "Email address detected.",
        Severity.HIGH,
    ),
    Rule(
        "phone_number",
        re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){9,15}(?!\w)"),
        "Phone-number-like value detected.",
        Severity.HIGH,
    ),
    Rule(
        "credit_card",
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        "Payment-card-like value detected.",
        Severity.CRITICAL,
    ),
)

SECRET_RULES = (
    Rule(
        "openai_key",
        re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
        "OpenAI-style API key detected.",
        Severity.CRITICAL,
    ),
    Rule(
        "aws_access_key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "AWS access-key-like value detected.",
        Severity.CRITICAL,
    ),
    Rule(
        "generic_secret",
        re.compile(r"\b(api[_ -]?key|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+-]{8,}", re.I),
        "Credential-like value detected.",
        Severity.CRITICAL,
    ),
)

HARM_RULES = (
    Rule(
        "malware_request",
        re.compile(r"\b(ransomware|credential stealer|keylogger|malware payload)\b", re.I),
        "Potential request for malicious software assistance.",
        Severity.CRITICAL,
    ),
    Rule(
        "physical_harm_request",
        re.compile(r"\b(build a bomb|poison someone|untraceable weapon)\b", re.I),
        "Potential request facilitating physical harm.",
        Severity.CRITICAL,
    ),
)


def scan_text(text: str, *, location: str, include_input_rules: bool = True) -> tuple[Finding, ...]:
    rules: tuple[Rule, ...] = PII_RULES + SECRET_RULES
    if include_input_rules:
        rules += INJECTION_RULES + HARM_RULES
    findings: list[Finding] = []
    for rule in rules:
        if rule.pattern.search(text):
            findings.append(
                Finding(
                    rule=rule.name,
                    message=rule.message,
                    severity=rule.severity,
                    location="input" if location == "input" else "output",
                )
            )
    return tuple(findings)


def redact_sensitive(text: str) -> str:
    redacted = text
    for rule in PII_RULES + SECRET_RULES:
        redacted = rule.pattern.sub(f"[REDACTED:{rule.name}]", redacted)
    return redacted
