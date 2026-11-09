"""Pulls the destination out of a free-form travel query."""

from functools import lru_cache

from src.agents.prompts import DESTINATION_EXTRACTION_PROMPT
from src.clients.llm import get_llm


@lru_cache(maxsize=128)
def extract_destination(query: str) -> str:
    """
    Cached in-memory: the same query maps to the same destination,
    avoiding redundant LLM calls on repeat queries.
    """

    prompt = DESTINATION_EXTRACTION_PROMPT.format(query=query)

    response = get_llm().invoke(prompt)

    return response.content.strip()
