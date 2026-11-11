# Roamly AI - Backend API ✈️

The backend service for **Roamly AI**, an agentic travel planning application powered by **FastAPI**, **LangGraph**, and **FastMCP**.

---

## 🏗️ Architecture

- **LangGraph Dynamic State Machine**:
  - **Supervisor Routing**: `router_agent` classifies user intent into three distinct paths:
    - **Path 1 (Guardrail & Boundary)**: `router_agent -> guardrail_agent -> END` for out-of-scope queries, missing origins, or ambiguous requests.
    - **Path 2 (Fast Local Advisor)**: `router_agent -> advisor_agent -> END` for context-grounded follow-up recommendations (e.g. local food, hidden spots) in 1 hop without rebuilding the itinerary.
    - **Path 3 (Planning Research Fan-Out)**: `router_agent -> scout_fanout -> [flight_agent, hotel_agent, weather_agent] -> itinerary_agent -> END`.
  - **Synchronization Barrier**: `itinerary_agent` synchronizes parallel research streams, builds daily schedules, and compiles the structured `TripPlan` directly to `END`.
- **Hybrid MCP (Model Context Protocol)**:
  - **Remote Streamable HTTP MCP**: Tavily search for real-time transit and accommodation scouting.
  - **Local Stdio FastMCP**: In-house FastMCP server (`src/mcp_servers/weather_server.py`) delivering structured multi-day forecasts and atmospheric observations via OpenWeather API.
- **Multi-Provider LLM Engine**:
  - Primary: Google Gemini (`gemini-3.8-flash`) with structured Pydantic schema validation.
  - Fallback: Groq high-speed inference running `llama-3.3-70b-versatile`.
- **Zero Hardcoding & Pre-Formulated Queries**:
  - Clean Pydantic domain models without regex, string slicing, or static heuristics.
  - Search queries pre-formulated during routing to minimize latency and token spend (5 LLM calls per full plan).
- **Thread Persistence**: In-memory `MemorySaver` checkpointer preserving state across conversational turns.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager

### 2. Setup Environment
```bash
cp .env.example .env
# Provide GEMINI_API_KEY (or GROQ_API_KEY), TAVILY_API_KEY, and OPENWEATHER_API_KEY in .env
```

### 3. Run Locally
```bash
uv run python main.py
```
- API server: **http://127.0.0.1:8000**
- Interactive Swagger docs: **http://127.0.0.1:8000/docs**
- Architecture map: **http://127.0.0.1:8000/architecture.html**

---

## 🐳 Docker Deployment

```bash
docker compose up -d
```
Container includes non-root least-privilege security (`app:app` UID 1001), multi-stage builds with `uv` layer caching, and automated healthcheck probes.
