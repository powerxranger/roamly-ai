"""Multi-provider LLM client with automatic fallback from Gemini to Groq."""

from functools import lru_cache
from typing import Any

from src.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_FALLBACK_MODEL,
    GROQ_MODEL,
)


@lru_cache(maxsize=1)
def _build_available_llms() -> list[tuple[str, Any]]:
    """Build list of available (provider_name, chat_model) pairs based on configured API keys."""
    clients: list[tuple[str, Any]] = []

    # Priority 1: Google Gemini (high free limits: 1500 requests/day)
    if GEMINI_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            gemini_client = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=GEMINI_API_KEY,
                temperature=0.2,
                max_retries=2,
            )
            clients.append((f"Gemini ({GEMINI_MODEL})", gemini_client))
        except Exception as e:
            print(f"[LLM] Warning: Failed to initialize Gemini client: {e}")

    # Priority 2: Groq (free open-source weights fallback)
    if GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq

            groq_primary = ChatGroq(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=0.2,
                max_retries=1,
                max_tokens=8192,
            )
            clients.append((f"Groq ({GROQ_MODEL})", groq_primary))

            if GROQ_FALLBACK_MODEL and GROQ_FALLBACK_MODEL != GROQ_MODEL:
                groq_secondary = ChatGroq(
                    model=GROQ_FALLBACK_MODEL,
                    api_key=GROQ_API_KEY,
                    temperature=0.2,
                    max_retries=2,
                    max_tokens=8192,
                )
                clients.append((f"Groq ({GROQ_FALLBACK_MODEL})", groq_secondary))
        except Exception as e:
            print(f"[LLM] Warning: Failed to initialize Groq client: {e}")

    return clients


@lru_cache(maxsize=1)
def get_llm():
    """Return a resilient LLM client with automatic fallbacks across configured providers."""
    available = _build_available_llms()
    if not available:
        raise ValueError(
            "No LLM API keys found. Please set GEMINI_API_KEY or GROQ_API_KEY in your .env file."
        )

    names = [name for name, _ in available]
    print(f"[LLM] Active providers: {' -> '.join(names)}")

    primary_name, primary_client = available[0]
    if len(available) > 1:
        fallbacks = [client for _, client in available[1:]]
        return primary_client.with_fallbacks(fallbacks)
    return primary_client


@lru_cache(maxsize=16)
def get_structured_llm(schema):
    """Return a structured output LLM runnable with automatic multi-provider fallbacks."""
    available = _build_available_llms()
    if not available:
        raise ValueError(
            "No LLM API keys found. Please set GEMINI_API_KEY or GROQ_API_KEY in your .env file."
        )

    structured_runnables = []
    for name, client in available:
        try:
            runnable = client.with_structured_output(schema, method="json_schema")
            structured_runnables.append(runnable)
        except Exception:
            runnable = client.with_structured_output(schema)
            structured_runnables.append(runnable)

    primary = structured_runnables[0]
    if len(structured_runnables) > 1:
        return primary.with_fallbacks(structured_runnables[1:])
    return primary

