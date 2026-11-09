"""Groq chat model configured from settings."""

from functools import lru_cache

from langchain_groq import ChatGroq

from src.config.settings import GROQ_MODEL, get_groq_api_key


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Return a shared Groq LLM client initialized with the environment API key."""
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=get_groq_api_key(),
        temperature=0.2,
        max_retries=3,
    )
