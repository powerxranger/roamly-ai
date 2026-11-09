"""In-memory checkpointer used by LangGraph to persist conversation threads."""

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver


@lru_cache(maxsize=1)
def get_checkpointer() -> MemorySaver:
    """Return a shared in-memory checkpointer for thread persistence."""
    return MemorySaver()
