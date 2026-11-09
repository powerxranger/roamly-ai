"""Fetches weather and forecast for the destination and emits structured WeatherPlan."""

import json
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import WEATHER_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.local import forecast_mcp_search, weather_mcp_search
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import WeatherPlan
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def _parse_weather_data(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if hasattr(raw, "content"):
        raw = raw.content
    if isinstance(raw, list) and len(raw) > 0:
        first = raw[0]
        if hasattr(first, "text"):
            raw = first.text
        elif isinstance(first, dict) and "text" in first:
            raw = first["text"]
        elif isinstance(first, dict):
            return first
    text = str(raw).strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        import ast
        val = ast.literal_eval(text)
        if isinstance(val, dict):
            return val
    except Exception:
        pass
    return {}


def weather_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("weather_model")
    existing_weather = state.get("weather_results", "")

    # Skip scouting if semantic supervisor determined climate intel is not needed
    if existing_weather and not intent.get("needs_weather", True):
        return {}

    destination = state.get("destination") or state.get("user_query", "")
    city = intent.get("primary_city") or destination
    if not city:
        raise RuntimeError("WeatherAgent requires a destination or primary city to retrieve weather data.")

    weather_plan = None
    weather_source = "openweather"
    llm_calls_made = 0

    # Step 1: Try local OpenWeather MCP tool first
    try:
        raw_current = run_async(weather_mcp_search(city))
        curr_dict = _parse_weather_data(raw_current)

        if "temperature_c" in curr_dict:
            raw_forecast = run_async(forecast_mcp_search(city))
            forecast_dict = _parse_weather_data(raw_forecast)

            current_summary = json.dumps(curr_dict, indent=2)
            forecast_summary = json.dumps(forecast_dict.get("forecast", forecast_dict), indent=2)
            weather_data = f"Current Observations:\n{current_summary}\n\nUpcoming Forecast:\n{forecast_summary}"

            structured_llm = get_llm().with_structured_output(WeatherPlan)
            prompt = WEATHER_STRUCTURED_PROMPT.format(
                destination=city,
                weather_data=weather_data,
            )

            weather_plan = structured_llm.invoke([
                SystemMessage(content="You are a helpful travel assistant. Do not invoke external file tools. Provide structured weather and packing data conforming to the schema."),
                HumanMessage(content=prompt),
            ])
            weather_plan.source = "openweather"
            weather_source = "openweather"
            llm_calls_made = 1
            print(f"[WeatherAgent] [Source: OpenWeather MCP] Retrieved and analyzed climate data for '{city}': {weather_plan.temperature}, {weather_plan.current_conditions}")
        else:
            print(f"[WeatherAgent] OpenWeather MCP returned no temperature data for '{city}'. Attempting fallback...")
    except Exception as e:
        print(f"[WeatherAgent] OpenWeather MCP error for '{city}': {e}. Attempting fallback...")
        weather_plan = None

    # Step 2: If OpenWeather is unavailable or failed, scout live weather via Tavily web search
    if weather_plan is None:
        try:
            print(f"[WeatherAgent] [Source: Tavily Live Search Fallback] Searching current weather for '{city}'...")
            search_query = f"current weather temperature and forecast in {city} climate conditions"
            weather_search_results = run_async(tavily_mcp_search(search_query))

            structured_llm = get_llm().with_structured_output(WeatherPlan)
            prompt = WEATHER_STRUCTURED_PROMPT.format(
                destination=city,
                weather_data=truncate(weather_search_results, 1500),
            )

            weather_plan = structured_llm.invoke([
                SystemMessage(content="You are a helpful travel assistant. Do not invoke external file tools. Provide structured weather and packing data conforming to the schema."),
                HumanMessage(content=prompt),
            ])
            weather_plan.source = "live_search"
            weather_source = "live_search"
            llm_calls_made = 1
            print(f"[WeatherAgent] [Source: Tavily Live Search Fallback] Successfully retrieved weather for '{city}': {weather_plan.temperature}, {weather_plan.current_conditions}")

        except Exception as e:
            if existing_model:
                weather_plan = WeatherPlan(**existing_model)
            else:
                raise RuntimeError(f"WeatherAgent failed to retrieve weather data for '{city}': {e}") from e

    model_dict = weather_plan.model_dump()
    source_label = "OpenWeather API" if weather_source == "openweather" else "Live Web Search (Tavily)"
    formatted_text = (
        f"Data Source: {source_label}\n"
        f"Current Conditions: {weather_plan.current_conditions}\n"
        f"Temperature: {weather_plan.temperature}\n"
        f"Forecast: {weather_plan.forecast_summary}\n\n"
        f"Packing Essentials:\n" +
        "\n".join(f"- {p}" for p in weather_plan.packing_list)
    )

    return {
        "weather_model": model_dict,
        "weather_results": formatted_text,
        "messages": [
            AIMessage(content=f"Weather intelligence fetched via {source_label}")
        ],
        "llm_calls": bump_llm_calls(state, llm_calls_made),
    }
