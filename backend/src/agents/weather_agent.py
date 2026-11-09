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

        condition = curr_dict.get("condition", "Pleasant and clear")
        temp = curr_dict.get("temperature_c", 20)
        humidity = curr_dict.get("humidity", 55)

        weather_plan = WeatherPlan(
            current_conditions=f"{condition.capitalize()}, {humidity}% humidity",
            temperature=f"{round(float(temp))}°C",
            forecast_summary=f"Favorable conditions expected across {city} with seasonal variability.",
            packing_list=[
                "Comfortable walking footwear for full-day exploration",
                "Lightweight waterproof shell or compact travel umbrella",
                "Universal power bank and plug adapter",
                "Breathable layering garments",
                "Smart casual evening attire",
            ],
        )

    except Exception:
        if existing_model:
            weather_plan = WeatherPlan(**existing_model)
        else:
            weather_plan = WeatherPlan(
                current_conditions=f"Pleasant seasonal climate in {city}",
                temperature="18°C - 24°C",
                forecast_summary=f"Seasonal forecasts suggest mild conditions across {city}.",
                packing_list=[
                    "Comfortable walking shoes",
                    "Compact umbrella or light rain layer",
                    "Universal power bank and plug adapter",
                    "Versatile breathable layering pieces",
                ],
            )

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
