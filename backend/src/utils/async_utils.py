"""Async utility helpers for Roamly AI graph execution."""

import asyncio
from typing import Awaitable, TypeVar

T = TypeVar("T")


def run_async(coroutine: Awaitable[T]) -> T:
    """Run a coroutine to completion from synchronous code (legacy helper)."""
    return asyncio.run(coroutine)


def bump_llm_calls(state: dict | None = None, count: int = 1) -> int:
    """Return the incremental LLM call count for the operator.add reducer."""
    return count
