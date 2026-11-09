"""Fetches weather and forecast for the destination and emits structured WeatherPlan."""

import json
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

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


def _generate_packing_list(temp_c: float, condition: str) -> list[str]:
    """Dynamically generate practical packing essentials based on live climate conditions."""
    items = ["Comfortable walking shoes"]
    cond_lower = condition.lower()

    if temp_c < 10:
        items.extend([
            "Heavy coat or insulated winter jacket",
            "Thermal innerwear and warm socks",
            "Beanie and warm gloves",
        ])
    elif temp_c < 20:
        items.extend([
            "Light jacket, fleece, or cardigan",
            "Long-sleeve shirts and comfortable pants",
        ])
    elif temp_c > 30:
        items.extend([
            "Breathable lightweight cotton or linen clothes",
            "Sunscreen (SPF 30+) and UV-blocking sunglasses",
            "Wide-brim sun hat or cap",
        ])
    else:
        items.extend([
            "Breathable casual shirts and comfortable trousers",
            "Light jacket or wrap for air-conditioned venues and evenings",
        ])

    if any(w in cond_lower for w in ("rain", "drizzle", "shower", "thunderstorm")):
        items.append("Compact travel umbrella or waterproof jacket")
    elif any(w in cond_lower for w in ("snow", "sleet", "ice")):
        items.append("Water-resistant winter boots")
    elif any(w in cond_lower for w in ("clear", "sun")):
        items.append("UV-protective sunglasses and hydrating lip balm")
    elif any(w in cond_lower for w in ("cloud", "overcast")):
        items.append("Versatile day-to-night layering essentials")

    items.append("Phone charger, travel adapter, and portable power bank")
    return items


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
    llm_calls_made = 0

    # Step 1: Try local OpenWeather MCP tool first
    try:
        raw_current = run_async(weather_mcp_search(city))
        curr_dict = _parse_weather_data(raw_current)

        if "temperature_c" in curr_dict:
            condition = str(curr_dict.get("condition", "clear")).capitalize()
            temp_num = float(curr_dict["temperature_c"])
            humidity = curr_dict.get("humidity", 50)

            weather_plan = WeatherPlan(
                current_conditions=f"{condition}, {humidity}% humidity",
                temperature=f"{round(temp_num)}°C",
                forecast_summary=f"Currently {condition.lower()} with temperatures around {round(temp_num)}°C and {humidity}% humidity across {city}.",
                packing_list=_generate_packing_list(temp_num, condition),
                source="openweather",
            )
            print(f"[WeatherAgent] [Source: OpenWeather MCP] Found weather for '{city}': {temp_num}°C, {condition}")
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
            weather_prompt = (
                f"Analyze the live web search results for the current weather in {city}.\n"
                f"Extract the real current meteorological conditions, temperature in Celsius (°C), forecast summary, and practical packing essentials.\n\n"
                f"Search Context:\n{truncate(weather_search_results, 1500)}"
            )

            weather_plan = structured_llm.invoke([
                SystemMessage(content="You are a helpful travel assistant. Do not invoke external file tools. Provide structured weather and packing data conforming to the schema."),
                HumanMessage(content=weather_prompt),
            ])
            weather_plan.source = "live_search"
            llm_calls_made = 1
            print(f"[WeatherAgent] [Source: Tavily Live Search Fallback] Successfully retrieved weather for '{city}': {weather_plan.temperature}, {weather_plan.current_conditions}")

        except Exception as e:
            if existing_model:
                weather_plan = WeatherPlan(**existing_model)
            else:
                raise RuntimeError(f"WeatherAgent failed to retrieve weather data for '{city}': {e}") from e

    model_dict = weather_plan.model_dump()
    source_label = "OpenWeather API" if weather_plan.source == "openweather" else "Live Web Search (Tavily)"
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
