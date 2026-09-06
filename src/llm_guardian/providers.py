from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from .models import EvalCase, ModelResponse


class Provider(Protocol):
    name: str
    model: str

    def generate(self, case: EvalCase) -> ModelResponse: ...


@dataclass
class ReplayProvider:
    """Replays committed fixtures so evaluation and CI are deterministic."""

    response_key: str
    model: str
    name: str = "deterministic-replay"

    def generate(self, case: EvalCase) -> ModelResponse:
        started = perf_counter()
        text = str(case.metadata[self.response_key])
        measured_ms = (perf_counter() - started) * 1000
        latency_ms = float(case.metadata.get(f"{self.response_key}_latency_ms", measured_ms))
        return ModelResponse(
            text=text,
            provider=self.name,
            model=self.model,
            latency_ms=latency_ms,
            input_tokens=len(case.prompt.split()),
            output_tokens=len(text.split()),
            cost_usd=float(case.metadata.get(f"{self.response_key}_cost_usd", 0.0)),
        )


@dataclass
class CallableProvider:
    """Adapter for local models, internal gateways, or test doubles."""

    fn: Callable[[EvalCase], str]
    model: str
    name: str = "callable"

    def generate(self, case: EvalCase) -> ModelResponse:
        started = perf_counter()
        text = self.fn(case)
        return ModelResponse(
            text=text,
            provider=self.name,
            model=self.model,
            latency_ms=(perf_counter() - started) * 1000,
        )


@dataclass
class OpenAIProvider:
    model: str = "gpt-4.1-mini"
    name: str = "openai"

    def generate(self, case: EvalCase) -> ModelResponse:
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Install llm-guardian[openai] for this adapter.") from exc
        client = OpenAI()
        evidence = "\n".join(f"[{index}] {item}" for index, item in enumerate(case.context, 1))
        prompt = f"Evidence:\n{evidence}\n\nRequest:\n{case.prompt}" if evidence else case.prompt
        started = perf_counter()
        result = client.responses.create(model=self.model, input=prompt)
        latency_ms = (perf_counter() - started) * 1000
        usage = getattr(result, "usage", None)
        return ModelResponse(
            text=result.output_text,
            provider=self.name,
            model=self.model,
            latency_ms=latency_ms,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )


@dataclass
class AnthropicProvider:
    model: str = "claude-3-5-haiku-latest"
    name: str = "anthropic"

    def generate(self, case: EvalCase) -> ModelResponse:
        try:
            from anthropic import Anthropic  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Install llm-guardian[anthropic] for this adapter.") from exc
        client = Anthropic()
        evidence = "\n".join(f"[{index}] {item}" for index, item in enumerate(case.context, 1))
        prompt = f"Evidence:\n{evidence}\n\nRequest:\n{case.prompt}" if evidence else case.prompt
        started = perf_counter()
        result = client.messages.create(
            model=self.model,
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (perf_counter() - started) * 1000
        text = "".join(
            block.text for block in result.content if getattr(block, "type", "") == "text"
        )
        return ModelResponse(
            text=text,
            provider=self.name,
            model=self.model,
            latency_ms=latency_ms,
            input_tokens=int(result.usage.input_tokens),
            output_tokens=int(result.usage.output_tokens),
        )
