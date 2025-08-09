from __future__ import annotations

import argparse
import os
from typing import Optional

from dotenv import load_dotenv  # type: ignore
from rich.console import Console  # type: ignore

from .agent import Agent
from .llm import create_llm
from .tools import get_available_tools


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal ReAct Agent CLI")
    parser.add_argument("query", type=str, help="Task or question for the agent")
    parser.add_argument(
        "--provider",
        type=str,
        default="mock",
        choices=["openai", "mock"],
        help="LLM provider to use",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name for the provider (e.g., gpt-4o-mini)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=3,
        help="Maximum reasoning/tool steps",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for the model",
    )
    return parser


def main() -> int:
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    # Fallback to mock if provider is openai but key missing
    provider: str = args.provider
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        Console().print("[yellow]OPENAI_API_KEY not set. Falling back to mock provider.[/yellow]")
        provider = "mock"

    llm = create_llm(provider)
    tools = get_available_tools()
    agent = Agent(llm=llm, tools=tools, max_steps=args.max_steps, temperature=args.temperature)

    Console().print(f"[bold]Provider[/bold]: {provider}")
    if args.model:
        Console().print(f"[bold]Model[/bold]: {args.model}")
    Console().print(f"[bold]Query[/bold]: {args.query}")
    Console().print("")

    final = agent.run(task=args.query, model=args.model)
    Console().print("\n[bold green]Final Answer:[/bold green]")
    Console().print(final)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())