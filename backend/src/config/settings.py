"""
Central configuration.

Everything that reads the environment lives here, so the rest of the
code never touches os.getenv directly.
"""

import os
from pathlib import Path

import certifi
from dotenv import load_dotenv

SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = SRC_DIR.parent

# Load .env from backend directory or current working directory
load_dotenv(PROJECT_DIR / ".env")
load_dotenv()

# Windows / corporate networks need an explicit CA bundle for outbound TLS.
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


# =========================
# API keys
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# =========================
# LLM Models & Providers
# =========================

# Primary: Google Gemini (high rate limits, 1,500 free requests/day)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Fallback: Groq (free open-source model fallback)
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")


# =========================
# Cross-origin (CORS)
# =========================

# Comma-separated origins allowed to call this API from a browser.
# Defaults to standard local frontend dev server ports (Vite 5173, Next 3000).
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]


def has_llm_key() -> bool:
    """Return True if at least one LLM provider key is configured."""
    return bool(GEMINI_API_KEY or GROQ_API_KEY)


def get_groq_api_key() -> str:
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Please add it to your .env file."
        )

    return GROQ_API_KEY
