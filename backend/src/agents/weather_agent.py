"""Fetches weather and forecast for the destination and emits structured WeatherPlan."""

import json
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import WEATHER_STRUCTURED_PROMPT
from src.clients.llm import get_structured_llm
from src.graph.state import TravelState
from src.mcp_servers.local import forecast_mcp_search, weather_mcp_search
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import WeatherPlan
from src.utils.async_utils import bump_llm_calls


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


async def weather_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("weather_model")

    # Skip scouting if semantic supervisor determined climate intel is not needed
    if not intent.get("needs_weather", True):
        return {}

    destination = state.get("destination") or state.get("user_query", "")
    city = intent.get("primary_city") or destination
    if not city:
        raise RuntimeError("WeatherAgent requires a destination or primary city to retrieve weather data.")

    timeline = intent.get("travel_dates") or state.get("travel_dates") or ""
    weather_data = ""
    weather_source = "openweather"

    # Step 1: Query local OpenWeather FastMCP tool for multi-day meteorological forecast
    try:
        raw_forecast = await forecast_mcp_search(city)
        forecast_dict = _parse_weather_data(raw_forecast)
        daily_items = forecast_dict.get("daily_forecast") or forecast_dict.get("forecast") or []

        if daily_items and isinstance(daily_items, list):
            day_lines = []
            for d in daily_items:
                if isinstance(d, dict):
                    day_label = f"{d.get('date', '')} ({d.get('day', '')})".strip()
                    temp_high = d.get("temp_max") or d.get("temperature", "")
                    temp_low = d.get("temp_min", "")
                    cond = d.get("weather") or d.get("condition", "Clear")
                    hum = d.get("humidity", "")
                    rain_p = d.get("rain_probability", "")

                    line_parts = [day_label]
                    if temp_high != "":
                        line_parts.append(f"Daytime: {temp_high}°C")
                    if temp_low != "":
                        line_parts.append(f"Low: {temp_low}°C")
                    line_parts.append(f"Conditions: {cond}")
                    if hum != "":
                        line_parts.append(f"Humidity: {hum}%")
                    if rain_p != "":
                        line_parts.append(f"Rain Probability: {rain_p}%")
                    day_lines.append(" - " + ", ".join(line_parts))

            timeline_header = f"Timeline: {timeline}" if timeline else "Upcoming trip window"
            weather_data = f"OpenWeather Multi-Day Forecast for {city} ({timeline_header}):\n" + "\n".join(day_lines)
            weather_source = "openweather"
            print(f"[WeatherAgent] [Source: OpenWeather MCP] Retrieved multi-day forecast for '{city}' ({len(daily_items)} days).")

        # If forecast had no daily items, try current weather
        if not weather_data:
            raw_current = await weather_mcp_search(city)
            curr_dict = _parse_weather_data(raw_current)
            if "temperature_c" in curr_dict:
                weather_data = (
                    f"Current Meteorological Readings from OpenWeather for {city}:\n"
                    f"- Temperature: {curr_dict.get('temperature_c')}°C\n"
                    f"- Atmospheric Condition: {curr_dict.get('condition')}\n"
                    f"- Humidity: {curr_dict.get('humidity')}%\n"
                    f"- Wind Speed: {curr_dict.get('wind_speed', 'N/A')} m/s"
                )
                weather_source = "openweather"
    except Exception as e:
        print(f"[WeatherAgent] OpenWeather MCP forecast error for '{city}': {e}. Attempting web search fallback...")

    # Step 2: Fallback to Tavily web search only if OpenWeather returned no data
    if not weather_data:
        try:
            print(f"[WeatherAgent] [Source: Tavily Live Search Fallback] Searching weather for '{city}' ({timeline or 'upcoming'})...")
            search_query = f"weather in {city} {timeline or 'forecast climate'} temperature rainfall packing"
            weather_search_results = await tavily_mcp_search(search_query)
            weather_data = str(weather_search_results) if weather_search_results else f"Seasonal climate and forecast for {city}."
            weather_source = "live_search"
        except Exception as e:
            if existing_model:
                weather_plan = WeatherPlan(**existing_model)
                model_dict = weather_plan.model_dump()
                return {
                    "weather_model": model_dict,
                    "weather_results": state.get("weather_results", ""),
                    "messages": [AIMessage(content="Preserved existing weather data.")],
                    "llm_calls": bump_llm_calls(state, 0),
                }
            raise RuntimeError(f"WeatherAgent failed to retrieve weather data for '{city}': {e}") from e

    # Single structured LLM call to build the WeatherPlan
    try:
        structured_llm = get_structured_llm(WeatherPlan)
        prompt = WEATHER_STRUCTURED_PROMPT.format(
            destination=city,
            travel_timeline=timeline or "Upcoming trip duration",
            weather_data=weather_data,
        )

        weather_plan: WeatherPlan = await structured_llm.ainvoke([
            SystemMessage(content="You are an expert travel assistant. Analyze the meteorological data and emit structured climate metrics and tailored packing recommendations for the specified timeline."),
            HumanMessage(content=prompt),
        ])
        weather_plan.timeline = timeline or None
        weather_plan.source = weather_source

    except Exception as e:
        if existing_model:
            weather_plan = WeatherPlan(**existing_model)
        else:
            raise RuntimeError(f"WeatherAgent failed to structure weather plan for '{city}': {e}") from e

    model_dict = weather_plan.model_dump()
    source_label = "OpenWeather API" if "openweather" in weather_source else "Live Web Search (Tavily)"
    timeline_header = f"Travel Timeline: {timeline}\n" if timeline else ""
    formatted_text = (
        f"Data Source: {source_label}\n"
        f"{timeline_header}"
        f"Conditions: {weather_plan.current_conditions}\n"
        f"Temperature: {weather_plan.temperature}\n"
        f"Forecast Outlook: {weather_plan.forecast_summary}\n\n"
        f"Packing Essentials:\n" +
        "\n".join(f"- {p}" for p in weather_plan.packing_list)
    )

    return {
        "weather_model": model_dict,
        "weather_results": formatted_text,
        "messages": [
            AIMessage(content=f"Weather intelligence fetched via {source_label}")
        ],
        "llm_calls": bump_llm_calls(state),
    }
