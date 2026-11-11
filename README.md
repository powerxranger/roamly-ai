# Roamly AI ✈️

A multi-agent AI travel planner powered by LangGraph. Describe the trip you want in plain English and get back flights, hotels, weather, and a complete day-by-day itinerary - researched for you in about a minute.

---

## 🧐 About

Planning a trip usually means juggling multiple browser tabs: one for flights, another for hotels, a third for weather, and a notes app trying to fit it all together. **Roamly AI** streamlines this into a unified agentic workflow.

You describe your travel desires in natural language:
> *"Plan a 7-day trip to Tokyo and Kyoto in late October for two people, mid-range budget, interested in food and temples"*

A team of specialized agents handles the research:
- 🧭 **Router Agent**: Analyzes travel intent, pre-formulates search queries, and selects the ideal execution path.
- 🛡️ **Guardrail Agent**: Intercepts out-of-scope queries and asks clarifying questions for ambiguous requests (e.g. missing origins).
- 💡 **Local Advisor Agent**: Fast 1-hop local recommendations and travel Q&A grounded in active itinerary context without full pipeline re-runs.
- ✈️ **Transit Agent**: Identifies multi-modal transit options across air, rail, and driving with fare ranges and route logistics.
- 🏨 **Hotel Agent**: Discovers accommodations matching destination, style, and budget parameters.
- 🌤️ **Weather Agent**: FastMCP-powered meteorological forecasts and climate-grounded packing tips.
- 🗺️ **Itinerary Agent**: Creates realistic daily schedules and directly synthesizes the complete, structured `TripPlan`.

---

## 🚀 Getting Started

### Prerequisites

- **Python >= 3.11**
- **[uv](https://docs.astral.sh/uv/)** (recommended package manager)
- **API Keys**:
  - [Google Gemini](https://aistudio.google.com/) (Primary LLM: gemini-3.8-flash) or [Groq](https://console.groq.com/) (Fallback LLM: llama-3.3-70b-versatile)
  - [Tavily](https://tavily.com/) (Web search for transit and hotels)
  - [OpenWeather](https://openweathermap.org/api) (Multi-day weather forecasts)

### Quick Start

#### 1. Backend (FastAPI + LangGraph)
```bash
cd backend
# Fill in your API keys in .env
cp .env.example .env

# Run FastAPI backend server
uv run python main.py
```
Backend API will be running at **http://127.0.0.1:8000** (Swagger docs at `/docs`).

#### 2. Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at **http://localhost:5173**.

---

## 🐳 Docker Deployment

To run via Docker Compose:

```bash
cd backend
docker compose up -d
```

---

## 🛠️ Architecture

- **Backend**: FastAPI, LangGraph, LangChain, FastMCP (Model Context Protocol)
- **Agent Orchestration**: Dynamic 3-path state machine:
  - Path 1: Guardrail short-circuit (`router_agent -> guardrail_agent -> END`)
  - Path 2: Fast advisor (`router_agent -> advisor_agent -> END`)
  - Path 3: Planning research fan-out (`router_agent -> scout_fanout -> [flight_agent, hotel_agent, weather_agent] -> itinerary_agent -> END`)
- **LLM Engine**: Multi-provider with Google Gemini (`gemini-3.8-flash`) as primary and Groq (`llama-3.3-70b-versatile`) as automated fallback
- **Data Integrations**:
  - Live Transit & Hotels: Tavily Search MCP
  - Weather & Forecasts: Custom OpenWeather FastMCP stdio server
- **Cost & Latency Optimization**: Streamlined scout execution with pre-formulated search queries (5 LLM calls per planning request)
- **State & Memory**: In-memory thread checkpointer (`MemorySaver`) via LangGraph
- **Frontend**: Modern React (Vite + TypeScript + Tailwind CSS) with live agent execution pipeline visualization, tabbed travel breakdown, and decoupled deployment (Vercel + Render)
