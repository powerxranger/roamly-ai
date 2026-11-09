"""Fetches weather and forecast for the destination and emits structured WeatherPlan."""

import json
from langchain_core.messages import AIMessage

from src.graph.state import TravelState
from src.mcp_servers.local import forecast_mcp_search, weather_mcp_search
from src.models.travel_models import WeatherPlan
from src.utils.async_utils import bump_llm_calls, run_async


def weather_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("weather_model")
    existing_weather = state.get("weather_results", "")

    # Skip scouting if semantic supervisor determined climate intel is not needed
    if existing_weather and not intent.get("needs_weather", True):
        return {}

    destination = state.get("destination") or state.get("user_query", "")
    city = intent.get("primary_city") or destination or "Tokyo"

    try:
        raw_current = run_async(weather_mcp_search(city))
        raw_forecast = run_async(forecast_mcp_search(city))

        # Parse dict/json from MCP tool
        curr_dict = raw_current if isinstance(raw_current, dict) else json.loads(str(raw_current)) if str(raw_current).startswith("{") else {}

        if "temperature_c" not in curr_dict:
            err_msg = curr_dict.get("message") or f"Invalid climate response for {city}"
            raise RuntimeError(f"Weather service returned error: {err_msg}")

        condition = curr_dict.get("condition", "clear")
        temp = curr_dict["temperature_c"]
        humidity = curr_dict.get("humidity", 50)

        weather_plan = WeatherPlan(
            current_conditions=f"{str(condition).capitalize()}, {humidity}% humidity",
            temperature=f"{round(float(temp))}°C",
            forecast_summary=f"Meteorological conditions across {city}.",
            packing_list=[
                "Comfortable walking footwear for full-day exploration",
                "Lightweight weather-appropriate layering garments",
                "Universal power bank and plug adapter",
                "Compact travel umbrella or rain protection",
            ],
        )

    except Exception as e:
        if existing_model:
            weather_plan = WeatherPlan(**existing_model)
        else:
            raise RuntimeError(f"WeatherAgent failed to retrieve climate data for '{city}': {e}") from e

    model_dict = weather_plan.model_dump()
    formatted_text = (
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
            AIMessage(content="Weather intelligence fetched")
        ],
        "llm_calls": bump_llm_calls(state, 0),
    }
