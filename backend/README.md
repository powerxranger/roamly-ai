# Roamly AI — Backend API ✈️

The backend service for **Roamly AI**, an agentic travel planning application powered by **FastAPI**, **LangGraph**, and **FastMCP**.

---

## 🏗️ Architecture

- **LangGraph Parallel Orchestration**:
  - `START -> [flight_agent, hotel_agent, weather_agent] -> itinerary_agent -> final_agent -> END`
  - Concurrent fan-out cuts retrieval latency by ~60%.
  - `itinerary_agent` acts as a synchronization barrier waiting for all 3 research streams before compiling the schedule.
- **Hybrid MCP (Model Context Protocol)**:
  - **Remote Streamable HTTP MCP**: Tavily search for real-time flight and hotel data.
  - **Local Stdio FastMCP**: In-house FastMCP server (`src/mcp_servers/weather_server.py`) wrapping OpenWeather API.
- **LLM Engine**: Groq high-speed inference running `llama-3.3-70b-versatile` (128k context, high TPM capacity).
- **Thread Persistence**: In-memory `MemorySaver` checkpointer for session state.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager

### 2. Setup Environment
```bash
cp .env.example .env
# Provide your GROQ_API_KEY, TAVILY_API_KEY, and OPENWEATHER_API_KEY in .env
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
