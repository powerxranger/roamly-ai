"""Tests for multi-provider LLM fallback architecture (Gemini -> Groq)."""

from unittest.mock import patch
from pydantic import BaseModel

from src.clients.llm import _build_available_llms, get_structured_llm
from src.config.settings import has_llm_key


class DummySchema(BaseModel):
    summary: str


def test_has_llm_key_with_gemini():
    with patch("src.config.settings.GEMINI_API_KEY", "test_gemini_key"):
        with patch("src.config.settings.GROQ_API_KEY", None):
            assert has_llm_key() is True


def test_has_llm_key_with_groq():
    with patch("src.config.settings.GEMINI_API_KEY", None):
        with patch("src.config.settings.GROQ_API_KEY", "test_groq_key"):
            assert has_llm_key() is True


def test_has_llm_key_empty():
    with patch("src.config.settings.GEMINI_API_KEY", None):
        with patch("src.config.settings.GROQ_API_KEY", None):
            assert has_llm_key() is False


def test_build_available_llms_priority_order():
    with patch("src.clients.llm.GEMINI_API_KEY", "test_gemini_key"):
        with patch("src.clients.llm.GROQ_API_KEY", "test_groq_key"):
            clients = _build_available_llms()
            assert len(clients) >= 2
            # Verify priority order: Gemini is first, Groq is fallback
            assert "Gemini" in clients[0][0]
            assert "Groq" in clients[1][0]


def test_get_structured_llm_fallback_chain():
    with patch("src.clients.llm.GEMINI_API_KEY", "test_gemini_key"):
        with patch("src.clients.llm.GROQ_API_KEY", "test_groq_key"):
            runnable = get_structured_llm(DummySchema)
            # Should be a RunnableWithFallbacks
            assert hasattr(runnable, "fallbacks")
            assert len(runnable.fallbacks) >= 1
