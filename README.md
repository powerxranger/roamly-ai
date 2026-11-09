# Roamly AI ✈️

A multi-agent AI travel planner powered by LangGraph. Describe the trip you want in plain English and get back flights, hotels, weather, and a complete day-by-day itinerary — researched for you in about a minute.

---

## 🧐 About

Planning a trip usually means juggling multiple browser tabs — one for flights, another for hotels, a third for weather, and a notes app trying to fit it all together. **Roamly AI** streamlines this into a unified agentic workflow.

You describe your travel desires in natural language:
> *"Plan a 7-day trip to Tokyo and Kyoto in late October for two people, mid-range budget, interested in food and temples"*

A team of specialized agents handles the research:
- ✈️ **Flights Agent**: Identifies departure/arrival airports, airlines serving routes, typical durations, and fare estimates.
- 🏨 **Hotel Agent**: Discovers accommodations matching your destination and budget parameters.
- 🌤️ **Weather Agent**: Gathers current conditions and forecasts to provide packing and season tips.
- 🗺️ **Itinerary Agent**: Creates realistic, day-by-day schedules with activity suggestions.
- 📋 **Final Synthesis Agent**: Blends all findings into a cohesive, structured travel plan.

---

## 🚀 Getting Started

### Prerequisites

- **Python >= 3.11**
- **[uv](https://docs.astral.sh/uv/)** (recommended package manager)
- **API Keys**:
  - [Groq](https://console.groq.com/) (LLM inference)
  - [Tavily](https://tavily.com/) (Web search for flights and hotels)
  - [OpenWeather](https://openweathermap.org/api) (Weather & forecasts)

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
- **Agent Orchestration**: Parallel fan-out / barrier fan-in graph (`START -> [flight_agent, hotel_agent, weather_agent] -> itinerary_agent -> final_agent -> END`)
- **LLM Engine**: Groq (high-speed inference with `llama-3.3-70b-versatile`)
- **Data Integrations**:
  - Live Flights & Hotels: Tavily Search MCP
  - Weather & Forecasts: Custom OpenWeather FastMCP server
- **State & Memory**: In-memory thread checkpointer (`MemorySaver`) via LangGraph
- **Frontend**: Modern React (Vite + TypeScript + Tailwind CSS) with live agent execution pipeline visualization, tabbed travel breakdown, and decoupled deployment (Vercel + Render)
