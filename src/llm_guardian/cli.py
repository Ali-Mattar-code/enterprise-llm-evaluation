from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .engine import EvaluationEngine, load_cases
from .gates import ReleaseGate
from .providers import (
    AnthropicProvider,
    GeminiProvider,
    OpenAIProvider,
    Provider,
    ReplayProvider,
)
from .reporting import write_json
from .scanners import redact_sensitive, scan_text

app = typer.Typer(help="Evaluate, red-team, and gate LLM releases.", no_args_is_help=True)
console = Console()


@app.command()
def evaluate(
    dataset: Annotated[
        Path, typer.Option(exists=True)
    ] = Path("datasets/evaluation_suite.jsonl"),
    provider: Annotated[
        str, typer.Option(help="replay, openai, anthropic, or gemini")
    ] = "replay",
    model: Annotated[str, typer.Option()] = "guarded-v2",
    response_key: Annotated[str, typer.Option()] = "candidate_response",
    output: Annotated[Path, typer.Option()] = Path("artifacts/local/run.json"),
) -> None:
    """Run an evaluation suite against a deterministic or live provider."""
    adapter: Provider
    if provider == "replay":
        adapter = ReplayProvider(response_key, model=model)
    elif provider == "openai":
        adapter = OpenAIProvider(model=model)
    elif provider == "anthropic":
        adapter = AnthropicProvider(model=model)
    elif provider == "gemini":
        adapter = GeminiProvider(model=model)
    else:
        raise typer.BadParameter("provider must be replay, openai, anthropic, or gemini")
    summary = EvaluationEngine().evaluate(load_cases(dataset), adapter)
    write_json(output, summary.to_dict())
    console.print(f"[bold]Pass rate:[/] {summary.pass_rate:.1%}")
    console.print(f"[bold]Critical failures:[/] {summary.critical_failures}")
    console.print(f"[bold]Saved:[/] {output}")


@app.command()
def gate(
    run: Annotated[Path, typer.Argument(exists=True)],
    config: Annotated[
        Path, typer.Option(exists=True)
    ] = Path("configs/release_gate.yaml"),
) -> None:
    """Inspect a saved run against a gate (use the demo for typed end-to-end gating)."""
    payload = json.loads(run.read_text(encoding="utf-8"))
    thresholds = ReleaseGate.from_yaml(config).config["thresholds"]
    table = Table("Measure", "Actual", "Threshold")
    table.add_row("pass_rate", f"{payload['pass_rate']:.3f}", f">= {thresholds['min_pass_rate']}")
    table.add_row(
        "critical_failures",
        str(payload["critical_failures"]),
        f"<= {thresholds['max_critical_failures']}",
    )
    console.print(table)


@app.command()
def scan(text: str, redact: bool = typer.Option(False, help="Print a redacted version.")) -> None:
    """Scan text for injection, PII, credential, and harmful-request indicators."""
    findings = scan_text(text, location="input")
    if not findings:
        console.print("[green]No configured rules matched.[/]")
    for finding in findings:
        console.print(f"[{finding.severity.value}] {finding.rule}: {finding.message}")
    if redact:
        console.print(redact_sensitive(text))


if __name__ == "__main__":
    app()
